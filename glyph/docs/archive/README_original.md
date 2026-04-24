# GFS-II: Reflexive Field System

A pocket-sized, enterprise-grade runtime where language = graph = runtime. 

## Overview
GFS-II is a unified symbolic computation substrate. The system operates entirely on Unicode glyphs representing nodes in an activation-based executable graph. It naturally supports self-modification, live trace viewing, and direct visual mapping.

## Structure
- `gfs.py`: The Python backend, containing the core Execution Engine, Graph structure, textual/graph parsing logic, and the HTTP Server for the IDE.
- `web/`: The Canvas-based visual IDE for real-time monitoring and manipulation.

## Core Glyphs
- **⟐** anchor (start)
- **⊢** emerge (task init)
- **⟡** transform (task logic)
- **⊣** resolve (task end)
- **⌁** trace (log)
- **⟳** loop (reactivate)

## Mutation Glyphs
- **✳** spawn (create node)
- **✂** delete (remove node)
- **⇄** rewire (change edges)
- **⌬** mutate (change glyph)
- **⤴** clone (duplicate node)
- **⤵** compress (remove node between)

## Usage

### CLI execution
```sh
# Run minimal target program
./gfs.py run

# Load specific file
./gfs.py run examples/target.gfs

# Step through explicitly
./gfs.py step
```

### Visual IDE
```sh
# Start web server on port 8080
./gfs.py serve
```
Open your browser to `http://localhost:8080/web/index.html` to view the live graph.