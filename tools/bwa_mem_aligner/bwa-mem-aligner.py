#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import argparse
from multiprocessing import cpu_count
import sys


def main():
    """ Main program """
    parser = argparse.ArgumentParser(description='BWA alignment')
    parser.add_argument('-i','--input-bam', dest='input_bam', type=str,
                        help='Input bam file', required=True)
    parser.add_argument('-r','--ref-genome', dest='ref_genome', type=str,
                        help='Reference genome file (eg, .fa.gz), make sure BWA index files '
                             '(eg. .alt, .ann, .bwt etc) are all present at the same location', required=True)
    parser.add_argument('-o','--output', dest='output', type=str,
                        help='Output bam file', required=True)
    parser.add_argument("-n", "--cpus", type=int, default=cpu_count())
    args = parser.parse_args()

    # retrieve the @RG from BAM header
    try:
        header = subprocess.check_output(['samtools', 'view', '-H', args.input_bam])

    except Exception as e:
        sys.exit('\n%s: Retrieve BAM header failed: %s' % (e, args.input_bam))

    # get @RG
    header_array = header.decode('utf-8').rstrip().split('\n')
    rg_array = []
    for line in header_array:
        if not line.startswith("@RG"): continue
        rg_array.append(line.rstrip().replace('\t', '\\t'))

    if not len(rg_array) == 1: sys.exit('\n%s: The input bam should only contain one readgroup ID: %s' % args.input_bam)

    sort_qname = 'samtools sort -n -O BAM -@ %s %s ' % (str(args.cpus), args.input_bam)

    bam2fastq = ' samtools fastq -@ %s - ' % (str(args.cpus))

    #Command with header
    alignment = ' bwa mem -K 100000000 -Y -t %s -p -R "%s" %s - ' % (str(args.cpus), rg_array[0], args.ref_genome)

    # Sort the SAM output by coordinate from bwa and save to BAM file
    sort_coordinate = ' samtools sort -O BAM -@ %s -o %s /dev/stdin' % (str(args.cpus), args.output)

    cmd = '|'.join([sort_qname, bam2fastq, alignment, sort_coordinate])

    print('command: %s' % cmd)
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

if __name__ == "__main__":
    main()
