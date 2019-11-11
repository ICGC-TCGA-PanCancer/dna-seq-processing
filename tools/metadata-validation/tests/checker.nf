#!/bin/bash nextflow

/*
 * Copyright (c) 2019, Ontario Institute for Cancer Research (OICR).
 *                                                                                                               
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

/*
 * author Junjun Zhang <junjun.zhang@oicr.on.ca>
 */

nextflow.preview.dsl=2

params.meta_format = "tsv"  // tsv or json
params.exp_json = ""  // optional json string of exp metadata
params.exp_tsv = "input/experiment-fq.tsv"
params.rg_tsv = "input/read_group-fq.tsv"
params.file_tsv = "input/file-fq.tsv"
params.seq_exp_json_name = "seq_exp-fq.json"
params.seq_rg_json_name = "seq_rg-fq.json"

include '../metadata-validation' params(params)

workflow {
  main:
    metadataValidation(
      params.meta_format,
      params.exp_json,
      file(params.exp_tsv),
      file(params.rg_tsv),
      file(params.file_tsv),
      params.seq_exp_json_name,
      params.seq_rg_json_name
    )
  publish:
    metadataValidation.out to: "outdir", mode: 'copy', overwrite: true
}
