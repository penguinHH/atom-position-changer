
# Atom Coordinates Changer

This is a Python-based desktop application built using **PyQt5** that allows users to load, modify, and save atomic coordinate files (e.g., Gaussian `.gjf` files). The application provides a user-friendly graphical interface for modifying the atomic coordinates of selected atoms within a specified range, with support for adjusting the X, Y, and Z axis values by a user-defined amount in Angstroms.

## Key Features:
- **Multi-language Support**: The application supports **English**, **Japanese**, and **Chinese (Simplified)**, allowing users to interact with the application in their preferred language.
- **Load and Save `.gjf` Files**: Easily load Gaussian input files, modify atom coordinates, and save the modified files.
- **Coordinate Modification**: Adjust atomic coordinates based on a range of selected atom numbers, with the ability to modify the X, Y, and/or Z axes independently.
- **Custom Header and Footer**: Add custom text for file headers and footers when saving modified files.

## Features in Detail:
- **Language Selector**: Users can choose between **English**, **Japanese**, or **Chinese** for the interface language.
- **Range Input**: Specify atom number ranges to apply changes to, using a simple range format (e.g., `1-5, 10-15`).
- **Coordinate Adjustment**: Users can enter a value to adjust atom coordinates by a specified amount in Angstroms.
- **File Handling**: Load `.gjf` files and save the modified files with custom headers and footers, making it ideal for computational chemistry workflows.

## Installation Instructions:
1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/atom-coordinates-changer.git
   ```
2. Install the necessary Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python AtomChangerGlobal.py
   ```

## License:
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
