## A simple GUI for viewing ADS-B data received with GNURadio

### Licence GPLV3

### Authors Thomas Lavarenne, Christophe Seguinot

### Features
This simple GUI was written in the objectives to: 
- Decode ADS-B frames received with a GNURadio ADS-B receiver
- Display decoded data in a table and on an OSM 'flight radar' map in real time
- running on any platform with GNURadio installed without the need to install/compile third apparty tool (no further dependancies needed)
- be compatible with python 2 and 3 versions
### Requirements
- in order to browse a "flight radar" map you must have a browser able to read local file i.e. bypassing the 'Same-Origin-Policy' For Local Files. This has been test with Chromium and can be configured in user preferences to use other browser.

### How-to
- Run gui_adsb.py (python gui_adsb.py)
- Read help and how-to tabs

### ToDo list
- implement unit conversion (partially done)
- improve adsb_receiver.grc flowgraph
  - test https://factorialabs.com/2018/05/ improved bloc correlate access code Tag with packet length
  - Test Paul Boven (Jive, Netherlands) solution using payload/header demux
  * test Cyrille Morin (INSA, Lyon) solution using a  "python bloc" (adsb_burst_divider.grc).
  * implement a self adjusted threshold in the OOK receiver
