class: CommandLineTool
cwlVersion: v1.0
id: seq-data-to-lane-bam
requirements:
- class: InlineJavascriptRequirement
- class: ShellCommandRequirement
- class: DockerRequirement
  dockerPull: 'quay.io/icgc-argo/dna-seq-processing-tools:seq-data-to-lane-bam.update'

baseCommand: [ 'seq-data-to-lane-bam.py' ]

inputs:
  seq_rg_json:
    type: File
    inputBinding:
      position: 2
      prefix: -p
  seq_files:
    type: File[]
    inputBinding:
      position: 3
      prefix: -d


outputs:
  lane_bams:
    type: File[]
    outputBinding:
      glob: '*.lane.bam'
  aligned_basename:
    type: string
    outputBinding:
      glob: preprocess.json
      loadContents: true
      outputEval: |
        ${
           var data = JSON.parse(self[0].contents)["aligned_basename"];
           return data;
         }
  bundle_type:
    type: string
    outputBinding:
      glob: preprocess.json
      loadContents: true
      outputEval: |
        ${
           var data = JSON.parse(self[0].contents)["bundle_type"];
           return data;
         }


stdout: preprocess.json

