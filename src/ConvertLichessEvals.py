import fnmatch
import json
import logging
import os
from pathlib import Path

from Utilities_Python import misc

CONFIG_FILE = os.path.join(Path(__file__).parents[1], 'config.json')


def build_file(file) -> str:
    reformat_file = f'{os.path.splitext(file)[0]}.lieval'
    if not os.path.isfile(reformat_file):
        with open(file, mode='r') as f:
            ct = 0
            for row in f:
                eval_json = json.loads(row)

                ct += 1
                if ct % 1000 == 0:
                    logging.info(f'processed {ct} records')

                fen = eval_json.get('fen')
                to_move = 'w' if 'w' in fen else 'b'
                evals = eval_json.get('evals')  # list of dictionaries
                for ev in evals:
                    knodes = ev.get('knodes')
                    depth = ev.get('depth')
                    pv_list = ev['pvs']  # list of principal variations
                    for pv in pv_list:
                        cp = pv.get('cp')
                        cp = '' if cp is None else cp
                        mate = pv.get('mate')
                        mate = '' if mate is None else mate
                        line = pv.get('line')

                        with open(reformat_file, mode='a') as wf:
                            # FEN / ToMove / KNodes / Depth / Evaluation / Mate / Line
                            wf.write(f'{fen}\t{to_move}\t{knodes}\t{depth}\t{cp}\t{mate}\t{line}\n')


def main():
    script_name = Path(__file__).stem
    _ = misc.initiate_logging(script_name, CONFIG_FILE, False)

    proc_dir = misc.get_config('processingDir', CONFIG_FILE)

    # build list of files to extract
    zst_files = []
    for f in os.listdir(proc_dir):
        if fnmatch.fnmatch(f, '*.zst'):
            zst_files.append(f)

    # extract and process files
    for f in zst_files:
        new_file_name = f.replace('.zst', '')
        cmd_text = f'zstd -d {f} -o {new_file_name}'
        logging.debug(cmd_text)
        if os.getcwd != proc_dir:
            os.chdir(proc_dir)
        os.system('cmd /C ' + cmd_text)

        build_file(os.path.join(proc_dir, new_file_name))


if __name__ == '__main__':
    main()
