#!/usr/bin/env python
import gspyce.simulation


def main():
    gspyce.simulation.SimulationGUI.from_cli_args().main()


if __name__ == '__main__':
    main()
