class: CommandLineTool
cwlVersion: v1.0
id: bam-merge-sort-markdup
requirements:
- class: InlineJavascriptRequirement
- class: ShellCommandRequirement
- class: DockerRequirement
  dockerPull: 'quay.io/icgc-argo/bam-merge-sort-markdup:bam-merge-sort-markdup.0.1.2'

baseCommand: [ 'bam-merge-sort-markdup.py' ]

inputs:
  aligned_lane_bams:
    type: File[]
    inputBinding:
      prefix: -i
  ref_genome:
    type: File
    inputBinding:
      prefix: -r
    secondaryFiles: [.fai]
  cpus:
    type: int?
    inputBinding:
      prefix: -n
  aligned_basename:
    type: string
    inputBinding:
      prefix: -o
  markdup:
    type: boolean
    inputBinding:
      prefix: -d
  cram:
    type: boolean
    inputBinding:
      prefix: -c

outputs:
  aligned_bam:
    type: File
    outputBinding:
      glob: $(inputs.aligned_basename).bam
    secondaryFiles: [.bai]
  aligned_bam_duplicate_metrics:
    type: File
    outputBinding:
      glob: $(inputs.aligned_basename).bam.duplicates-metrics.txt
  aligned_cram:
    type: File
    outputBinding:
      glob: $(inputs.aligned_basename).cram
    secondaryFiles: [.crai]
  bundle_type:
    type: string
    outputBinding:
      glob: stdout.json
      loadContents: true
      outputEval: |
        ${
           var data = JSON.parse(self[0].contents)["bundle_type"];
           return data;
         }

stdout: stdout.json



