Current release <0.1a1>
=======================

## Proposed benchmarks for 0.1 alpha 1

### Already implemented:

  - Support for sockets commands in JSON format vs CSV
  - Static argument typing for the CPUInterpreter
  - Data pagination (starting point) for faster update fetching
  - Option to save file in memory or disk
  - Live data storage in memory; file dumping at the end
  - Implementation's configuration in a JSON file
  - Support for multiple sensors functioning at a time
  - Flexible settings configuration: dynamic settings, 
  configuration settings, and default (coded) settings
  - Simple, working logging features that can be used regardless
  of whether the framework's architecture is being used, or only
  the library.
  - CLI commands support allowing dynamic subparsing
  - Pre-set configuration file generator easily editable with a
  stub file.
  - Asynchrony modules: processes and threads, pipes, managers, etc.
  - Shared queues to easily synchronize data
 
### Not implemented:
  
  - Automatic data dumping to a file with custom frequency or when 
  memory gets full
  - UploaderUnit integration with SamplingUnit to upload file 
  - Data cleanup for SensorBaseReader data list (after data was 
  uploaded or dumped to file) to release memory storage and speed 
  up operations
  and remove temporary data (and real-time file upload)
  - Easy pre-set features for a LocalUI development (not from 
  scratch)
  - Fully functional logging architecture
  - Upload log files
  - Starting daemons
  - Installation tool
  - Upload logs

### Current issues:
  -  <#3> [Decorator inheritance in abc subclassing](https://github.com/Rocamonde/savannah-framework/issues/3)

----------

Other releases
==============

Features description for other than the current release:

## Draft for 0.1 alpha 2

  - Real-time log messages to remote location
  - Apart from log files, real-time simple status information
   about the sensors (functioning/not functioning, 
   operational/not operational)
  - Server-side API
  - User authentication (AuthUnit): NFC and Bluetooth
 

## Non-scheduled enhancement proposals for future versions

  - Sensors that support other data types that cannot be
   easily stored in simple lists (images, sound, etc)
  - Support for workers to process data upload simultaneously 
  in different cores for infrastructures that require 
  super-fast no-delay monitoring (only functional with 
  high-speed internet connection access)
