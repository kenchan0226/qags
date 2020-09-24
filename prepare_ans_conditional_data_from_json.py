import os
import sys
import json
import random
import argparse
from collections import defaultdict, Counter
from os.path import join
import re


ANS_TOK = "[ANS]"
NO_ANS_TOK = "[NO_ANS]"


def _count_data(path):
    """ count number of data in the given path"""
    matcher = re.compile(r'[0-9]+\.json')
    match = lambda name: bool(matcher.match(name))
    names = os.listdir(path)
    n_data = len(list(filter(match, names)))
    return n_data



def prepare_ans_conditional_data_from_json(data_dir,
                                 out_dir,
                                 out_prefix,
                                 ):

    txt_w_ans_file = f"{out_dir}/{out_prefix}_w_ans.txt"
    txt_file = f"{out_dir}/{out_prefix}.txt"
    ans_file = f"{out_dir}/{out_prefix}_ans.txt"

    # extract reference entities as answer

    dummy_txt = "Both sets of research findings were published Thursday ."
    dummy_answer = ["Thursday"]

    n_data = _count_data(data_dir)
    all_txts = []
    all_anss = []
    for i in range(n_data):
        with open(join(data_dir, '{}.json'.format(i))) as f:
            js = json.loads(f.read())
            doc_sent_list = js['article']
            summary_sent_list = js['abstract']

            if doc_sent_list and summary_sent_list:
                summary_str = " ".join(summary_sent_list)
                reference_entities = js['reference_entity_list_non_numerical']
                reference_entities = list(set(reference_entities))
                all_txts.append(summary_str)
                all_anss.append(reference_entities)
            else:
                # handle empty input, put a dummy sentence and answer.
                all_txts.append(dummy_txt)
                all_anss.append(dummy_answer)

    assert len(all_txts) == len(all_anss) == n_data

    print("Writing...")
    txts_w_ans = list()
    all_txt = list()
    all_ans = list()
    for txt, anss in zip(all_txts, all_anss):
        for ans in anss:
            txts_w_ans.append(f"{txt} {ANS_TOK} {ans}")
            all_txt.append(txt)
            all_ans.append(ans)

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    with open(txt_w_ans_file, 'w') as out_fh:
        for txt in txts_w_ans:
            out_fh.write(f'{txt}\n')
    with open(txt_file, 'w') as out_fh:
        for txt in all_txt:
            out_fh.write(f'{txt}\n')
    with open(ans_file, 'w') as out_fh:
        for ans in all_ans:
            out_fh.write(f'{ans}\n')
    print("\tDone!")
    print(f"\tWrote {len(txts_w_ans)} sentences to {txt_w_ans_file}")


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--data_dir", type=str, help=".")
    parser.add_argument("--split", type=str, help=".")
    parser.add_argument("--out_dir", type=str, help="Directory to write outputs")
    parser.add_argument("--out_prefix", type=str, default="test", help="Prefix for files written out")

    args = parser.parse_args()

    split_dir = join(args.data_dir, args.split)

    prepare_ans_conditional_data_from_json(split_dir, args.out_dir, args.out_prefix)

if __name__ == '__main__':
    main()
