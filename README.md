Here’s a clean, professional **README.md** draft for your repo:

---

# AoA\_Visualizer

📡 **AoA\_Visualizer** is a Python-based tool to analyze and visualize experimental and calculated **Angle of Arrival (AoA)** measurements for drones and anchors, based on RSSI and position data.
It supports calculating real azimuth and elevation angles with respect to defined anchor positions, comparing against experimental measurements, and producing insightful plots and error analysis.

---

## 📂 Features

✅ Reads CSV datasets with drone positions, peer MACs, experimental azimuth & elevation.
✅ Computes real azimuth & elevation angles with respect to each anchor’s frame of reference.
✅ Compares real vs experimental angles.
✅ Computes errors and aggregates by unique `(x, y, z)` points.
✅ Identifies best, average, and worst points based on error.
✅ Visualizes:

* Histograms of errors
* Bar charts of real vs experimental angles at key points
  ✅ Generates clean CSV summary files.

---

## 📈 Example Outputs

* CSV: `average_angles_and_errors.csv` with mean angles & errors per point.
* Plots:

  * Histograms of azimuth and elevation errors.
  * Bar charts comparing real vs experimental angles at best, average, worst points.

---

## 🚀 How to Use

### 🔧 Requirements

* Python 3.8+
* Install dependencies:

```bash
pip install -r requirements.txt
```

### 📥 Input

Prepare a CSV file (example: `Experiment1(50).csv`) with columns:

```
drone_x, drone_y, drone_z, peer_mac, azimuth, elevation, rssi, …
```

Place the file in the repository directory.

### ▶️ Run

Run the main analysis script:

```bash
python analyze_angles.py
```

This will:
✅ Generate `average_angles_and_errors.csv`
✅ Display plots
✅ Print key points (best/avg/worst) in the terminal

---

## 📊 Output Files

| File                            | Description                                                  |
| ------------------------------- | ------------------------------------------------------------ |
| `average_angles_and_errors.csv` | Summary table of real & experimental angles and their errors |
| Plots                           | Shown on screen                                              |

---

## 📝 Repository Structure

```
AoA_Visualizer/
├── analyze_angles.py        # Main analysis script
├── Experiment1(50).csv      # Example input data
├── README.md                 # Documentation
└── requirements.txt          # Python dependencies
```

---

## ✨ TODO / Future Work

* Add command-line interface
* Support batch processing of multiple CSVs
* Save plots automatically to files
* Improve customization of anchor positions

---

## 👤 Author

[**Arya S Patil**](https://github.com/Arya-S-Patil)

---

If you’d like, I can also:
✅ generate a `requirements.txt`
✅ write an example `analyze_angles.py` stub with CLI


