# Traffic Simulation Project 🚗

A Pygame-based traffic simulation i wrote for my seminar work in 2023.

## Overview 🌐
This project consists of three core components:
1. **header.py**: Defines data structures for junctions, streets, traffic lights, and map configurations.
2. **scraper.py**: Fetches and processes OpenStreetMap data to generate a simulation-ready map (saved as `map.json`).
3. **simulation.py**: Runs an interactive visualization of traffic flow with configurable parameters.

## Features ✨
- Real-world map integration via OpenStreetMap API
- Traffic light phase control with customizable timing
- Vehicle spawning, pathfinding, and collision avoidance
- Metrics tracking (e.g., vehicle density)
- Adjustable simulation speed and visualization settings

## Installation 🛠️
1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/traffic-simulation.git
   cd traffic-simulation
2. **Install dependencies**:
   ```bash
   pip install pygame