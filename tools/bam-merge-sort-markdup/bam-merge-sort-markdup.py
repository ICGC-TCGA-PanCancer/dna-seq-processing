#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import subprocess
import argparse
from multiprocessing import cpu_count
import json
import os

def run_cmd(cmd):
  stdout, stderr, p, success = '', '', None, True
  try:
    p = subprocess.Popen([cmd],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          shell=True)
    stdout, stderr = p.communicate()
  except Exception as e:
    print('Execution failed: %s' % e, file=sys.stderr)
    success = False

  if p and p.returncode != 0:
    print('Execution failed, none zero code returned.', file=sys.stderr)
    success = False

  print(stdout.decode("utf-8"))
  print(stderr.decode("utf-8"), file=sys.stderr)

  if not success:
    sys.exit(p.returncode if p.returncode else 1)

  return stdout, stderr

def main():
    """ Main program """
    parser = argparse.ArgumentParser(description='Merge and markdup')
    parser.add_argument('-i','--input-bams', dest='input_bams',
                        type=str, help='Input bam file', nargs='+', required=True)
    parser.add_argument('-b','--output-base', dest='output_base',
                        type=str, help='Output merged file basename', required=True)
    parser.add_argument('-r', '--reference', dest='reference',
                        type=str, help='reference fasta', required=True)
    parser.add_argument("-n", "--cpus", dest='cpus', type=int, default=cpu_count())
    parser.add_argument("-d", "--mdup", dest='mdup', action='store_true')
    parser.add_argument("-l", "--lossy", dest='lossy', action='store_true')
    parser.add_argument("-o", "--output-format", dest='output_format', choices=['bam', 'cram'], default=['cram'], nargs='+')

    args = parser.parse_args()

    cmd = []

    if args.mdup:
        merge = 'bammarkduplicates2 markthreads=%s O=/dev/stdout M=%s I=%s ' % \
                (str(args.cpus), args.output_base + ".duplicates-metrics.txt", ' I='.join(args.input_bams))
    else:
        merge = 'samtools merge -uf -@ %s /dev/stdout %s ' % (args.cpus, ' '.join(args.input_bams))

    if args.lossy:
        cram = 'java -jar /tools/cramtools.jar cram -R %s --capture-all-tags --lossy-quality-score-spec \*8 --preserve-read-names -O %s' % (args.reference, args.output_base + ".cram")
    else:
        cram = 'samtools view -C -T %s -@ %s /dev/stdin -o %s ' % (args.reference, args.cpus, args.output_base + ".cram")

    tee = 'tee %s ' % (args.output_base + ".bam")
    bai = 'samtools index -@ %s /dev/stdin %s' % (args.cpus, args.output_base + ".bam.bai")
    bai1 = 'samtools index -@ %s %s %s ' % (args.cpus, args.output_base + ".bam", args.output_base + ".bam.bai")
    crai1 = 'samtools index -@ %s %s %s ' % (args.cpus, args.output_base + ".cram", args.output_base + ".cram.crai")
    tgz = 'tar czf %s.duplicates-metrics.tgz %s.duplicates-metrics.txt' % (args.output_base, args.output_base)

    # build command
    if "bam" in args.output_format and "cram" in args.output_format:
        cmd.append('|'.join([merge, tee, cram]))
        cmd.append(bai1)
        cmd.append(crai1)

    elif "bam" in args.output_format and not "cram" in args.output_format:
        cmd.append('|'.join([merge, tee, bai]))

    elif not "bam" in args.output_format and "cram" in args.output_format:
        cmd.append('|'.join([merge, cram]))
        cmd.append(crai1)
    else:
        sys.exit("Unsupported sequence format!")

    for c in cmd:
       run_cmd(c)

    if os.path.isfile(os.path.join(os.getcwd(), args.output_base + ".duplicates-metrics.txt")):
       run_cmd(tgz)

    # write the parameter to stdout
    output = {"bundle_type": "dna_alignment"}
    print(json.dumps(output))


if __name__ == "__main__":
    main()
