Here come the datamodel files for this module

## datamodel code architecture

The datamodel code folder is organized with a few folders :

* .docker
  * .pg_service.conf
* app : all files related to the application schema
* changelogs : all base datamodel files (ordinary data, value lists, system tables)
  * YYYY.X.Z : Folders of each specific versions with their deltas (additionnal changes)
* demo_data : Demo data files in .sql format
* scripts : useful scripts for assets creation
* tests : unit tests of the datamodel features

and files :
* .pum.yaml : Central pum file of the module
  Contains main informations about the module name, parameters, ...
See [PUM documentation for more information](https://opengisch.github.io/pum/configuration/configuration/)

