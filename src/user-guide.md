# User Guide For Pyarmor v4

This is the documentation for Pyarmor 3.4 and later.

## Introduction

## Usage

### Obfuscate Python Scripts

  first time: obfuscate
  script updated: build
  fly options: obfuscate --no-save
  show options: info
  update options: config
  
### Use Project to Manage Obfuscated Scripts

  init
  
### Distribute Obfuscated Scripts

#### License of Obfuscated Scripts

#### Cross Platform

The core of [Pyarmor] is written by C, the only dependency is libc. So
it's not difficult to build for any other platform, even for embeded
system. Contact <jondy.zhao@gmail.com> if you'd like to run encrypted
scripts in other platform.

The latest platform-depentent library could be
found [here](http://pyarmor.dashingsoft.com/downloads/platforms)

### Examples

#### odoo

#### py2exe

## Benchmark Test

## Configure File

        ( 'version', '.'.join([str(x) for x in VERSION]) ), \
        ( 'name', None ), \
        ( 'src', None ), \
        ( 'manifest', default_manifest_template ), \
        ( 'entry', None ), \
        ( 'output', default_output_path ), \
        ( 'capsule', capsule_filename ), \
        ( 'runtime_path', None ), \
        ( 'obf_module_mode', default_obf_module_mode ), \
        ( 'obf_code_mode', default_obf_code_mode )

## Command Options

init, config, build, info, check, licenses, hdinfo, benchmark
