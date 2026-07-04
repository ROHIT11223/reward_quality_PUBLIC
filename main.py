import sys
import os
import pandas as pd
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QSpinBox, QPushButton, QGridLayout, QMessageBox, QFileDialog, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont, QIcon

class QualityRewardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quality Reward System v1.1 - Smart Resume")
        self.setMinimumSize(850, 750)
        
        # State
        self.config_data = {'rdes': [], 'errors': []}
        self.current_counts = {}
        
        # Apply Dark Mode Stylesheet
        self.setStyleSheet("""
            QMainWindow { background-color: #0f172a; }
            QLabel { color: #f8fafc; font-family: 'Inter', sans-serif; }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #1e293b; color: #f8fafc;
                border: 1px solid #334155; border-radius: 5px;
                padding: 8px; font-size: 14px;
            }
            QPushButton {
                background-color: #3b82f6; color: white; border: none;
                border-radius: 5px; padding: 10px 15px; font-weight: bold; font-size: 14px;
            }
            QPushButton:hover { background-color: #2563eb; }
            QPushButton#counterBtn {
                background-color: #334155; color: #f8fafc; font-size: 16px;
                font-weight: bold; border-radius: 4px; padding: 5px 10px;
            }
            QPushButton#counterBtn:hover { background-color: #475569; }
            QPushButton#successBtn { background-color: #10b981; }
            QPushButton#successBtn:hover { background-color: #059669; }
            QScrollArea { border: none; background-color: transparent; }
            QWidget#scrollWidget { background-color: #0f172a; }
        """)

        self.initUI()
        
        # Auto-load config if it exists
        default_config = os.path.join("support_files", "Config_Template.csv")
        if os.path.exists(default_config):
            self.load_config(default_config)

    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # --- Header ---
        header_layout = QHBoxLayout()
        
        logo_label = QLabel()
        logo_path = os.path.join("support_files", "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        else:
            logo_label.setText("[ QR ]")
            logo_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
            logo_label.setStyleSheet("color: #3b82f6;")
            
        header_layout.addWidget(logo_label)
        
        title_layout = QVBoxLayout()
        title_label = QLabel("Quality Reward System")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #60a5fa;")
        
        version_label = QLabel("v1.1.0 - Smart Resume Edition")
        version_label.setStyleSheet("color: #94a3b8;")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(version_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        load_config_btn = QPushButton("Load Config Excel/CSV")
        load_config_btn.clicked.connect(self.browse_config)
        header_layout.addWidget(load_config_btn)
        
        main_layout.addLayout(header_layout)

        # --- Form Inputs ---
        form_layout = QHBoxLayout()
        
        doc_layout = QVBoxLayout()
        doc_layout.addWidget(QLabel("Document Name:"))
        self.doc_input = QLineEdit()
        self.doc_input.setPlaceholderText("Enter document name...")
        doc_layout.addWidget(self.doc_input)
        form_layout.addLayout(doc_layout)
        
        rde_layout = QVBoxLayout()
        rde_layout.addWidget(QLabel("User Name (RDE):"))
        self.rde_select = QComboBox()
        rde_layout.addWidget(self.rde_select)
        form_layout.addLayout(rde_layout)

        rev_layout = QVBoxLayout()
        rev_layout.addWidget(QLabel("Review Number:"))
        self.rev_input = QSpinBox()
        self.rev_input.setMinimum(1)
        self.rev_input.setMaximum(999)
        rev_layout.addWidget(self.rev_input)
        form_layout.addLayout(rev_layout)
        
        check_layout = QVBoxLayout()
        check_layout.addWidget(QLabel("")) # Spacer
        self.check_btn = QPushButton("Check / Resume")
        self.check_btn.setStyleSheet("background-color: #8b5cf6;")
        self.check_btn.clicked.connect(self.check_resume)
        check_layout.addWidget(self.check_btn)
        form_layout.addLayout(check_layout)

        main_layout.addLayout(form_layout)

        # --- Errors Section ---
        errors_label = QLabel("Error Tracking")
        errors_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        main_layout.addWidget(errors_label)

        # Scroll Area for Errors
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_widget.setObjectName("scrollWidget")
        self.errors_layout = QGridLayout(self.scroll_widget)
        self.errors_layout.setVerticalSpacing(15)
        self.errors_layout.setHorizontalSpacing(30)
        scroll_area.setWidget(self.scroll_widget)
        main_layout.addWidget(scroll_area)

        # --- Bottom Section ---
        bottom_layout = QHBoxLayout()
        
        bonus_layout = QHBoxLayout()
        bonus_layout.addWidget(QLabel("Bonus Points:"))
        self.bonus_input = QLineEdit("0")
        self.bonus_input.setFixedWidth(80)
        self.bonus_input.textChanged.connect(self.update_score)
        bonus_layout.addWidget(self.bonus_input)
        bottom_layout.addLayout(bonus_layout)
        
        bottom_layout.addStretch()
        
        score_label = QLabel("Calculated Points:")
        score_label.setFont(QFont("Arial", 14))
        bottom_layout.addWidget(score_label)
        
        self.score_display = QLabel("0")
        self.score_display.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.score_display.setStyleSheet("color: #10b981;")
        bottom_layout.addWidget(self.score_display)
        
        main_layout.addLayout(bottom_layout)

        # --- Actions ---
        actions_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save (Pending)")
        self.save_btn.setMinimumHeight(45)
        self.save_btn.clicked.connect(lambda: self.save_record(is_final=False))
        
        self.submit_btn = QPushButton("Submit (Final)")
        self.submit_btn.setObjectName("successBtn")
        self.submit_btn.setMinimumHeight(45)
        self.submit_btn.clicked.connect(lambda: self.save_record(is_final=True))
        
        actions_layout.addWidget(self.save_btn)
        actions_layout.addWidget(self.submit_btn)
        main_layout.addLayout(actions_layout)

    def browse_config(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Config File", "", "Excel Files (*.xlsx *.xls);;CSV Files (*.csv)")
        if file_path:
            self.load_config(file_path)

    def load_config(self, file_path):
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
                
            self.config_data['rdes'] = df['RDE_Name'].dropna().unique().tolist()
            
            # Extract up to 10 errors
            errors_df = df[['Error_Name', 'Error_Weight']].dropna()
            self.config_data['errors'] = errors_df.head(10).to_dict('records')
            
            self.populate_ui()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load config: {str(e)}")

    def populate_ui(self):
        # Populate RDE
        self.rde_select.clear()
        self.rde_select.addItems(self.config_data['rdes'])
        
        # Clear existing errors layout
        for i in reversed(range(self.errors_layout.count())): 
            widget = self.errors_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                
        self.current_counts.clear()
        
        row = 0
        col = 0
        for idx, error in enumerate(self.config_data['errors']):
            err_id = f"error_{idx}"
            self.current_counts[err_id] = 0
            
            err_widget = QWidget()
            err_widget.setStyleSheet("QWidget { background-color: rgba(255, 255, 255, 0.05); border-radius: 8px; }")
            err_layout = QHBoxLayout(err_widget)
            
            info_layout = QVBoxLayout()
            name_label = QLabel(error['Error_Name'])
            name_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            weight_label = QLabel(f"Weight: {error['Error_Weight']}")
            weight_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
            info_layout.addWidget(name_label)
            info_layout.addWidget(weight_label)
            err_layout.addLayout(info_layout)
            err_layout.addStretch()
            
            minus_btn = QPushButton("-")
            minus_btn.setObjectName("counterBtn")
            minus_btn.setFixedSize(35, 35)
            
            count_label = QLabel("0")
            count_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            count_label.setFixedWidth(30)
            
            plus_btn = QPushButton("+")
            plus_btn.setObjectName("counterBtn")
            plus_btn.setFixedSize(35, 35)
            
            def make_handler(eid, clabel, delta):
                def handler():
                    new_val = self.current_counts[eid] + delta
                    if new_val >= 0:
                        self.current_counts[eid] = new_val
                        clabel.setText(str(new_val))
                        self.update_score()
                return handler

            minus_btn.clicked.connect(make_handler(err_id, count_label, -1))
            plus_btn.clicked.connect(make_handler(err_id, count_label, 1))
            
            err_layout.addWidget(minus_btn)
            err_layout.addWidget(count_label)
            err_layout.addWidget(plus_btn)
            
            self.errors_layout.addWidget(err_widget, row, col)
            
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        self.update_score()

    def update_score(self):
        score = 0
        try:
            bonus = float(self.bonus_input.text())
        except ValueError:
            bonus = 0
            
        score += bonus
        for idx, error in enumerate(self.config_data['errors']):
            err_id = f"error_{idx}"
            count = self.current_counts.get(err_id, 0)
            weight = float(error['Error_Weight'])
            score += (count * weight)
            
        self.score_display.setText(f"{score:g}")
        if score < 0:
            self.score_display.setStyleSheet("color: #ef4444;") # Red
        else:
            self.score_display.setStyleSheet("color: #10b981;") # Green

    def _get_unique_key(self):
        doc = self.doc_input.text().strip()
        rde = self.rde_select.currentText()
        rev = str(self.rev_input.value())
        return doc, rde, rev

    def check_resume(self):
        doc, rde, rev = self._get_unique_key()
        if not doc:
            QMessageBox.warning(self, "Validation", "Please enter a Document Name first.")
            return

        file_path = "Records.xlsx"
        if not os.path.exists(file_path):
            QMessageBox.information(self, "Info", "No database found. You can start a new record.")
            return

        try:
            df = pd.read_excel(file_path)
            
            # Filter by the unique key (Doc + RDE + Rev)
            mask = (
                (df['Document_Name'] == doc) & 
                (df['RDE_Name'] == rde) & 
                (df['Review_Number'].astype(str) == rev)
            )
            
            if not mask.any():
                QMessageBox.information(self, "Info", "No existing record found. You can start fresh.")
                return
                
            reply = QMessageBox.question(
                self, 
                "Record Found", 
                "This document and review number already exist for this user in the database. Do you want to resume?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                row = df[mask].iloc[0]
                
                # Restore Bonus
                try:
                    bonus_val = str(row['bonus_point'])
                    if bonus_val != 'nan':
                        self.bonus_input.setText(bonus_val)
                except:
                    pass

                # Restore Errors
                for idx, error in enumerate(self.config_data['errors']):
                    col_name = f"Error_{idx+1}_({error['Error_Name']})"
                    if col_name in row:
                        val = row[col_name]
                        if pd.notna(val):
                            self.current_counts[f"error_{idx}"] = int(val)
                
                # Update UI Counters
                for i in range(self.errors_layout.count()):
                    widget = self.errors_layout.itemAt(i).widget()
                    if widget:
                        # Extract error index from layout position
                        row_idx, col_idx, _, _ = self.errors_layout.getItemPosition(i)
                        linear_idx = (row_idx * 2) + col_idx
                        if linear_idx < len(self.config_data['errors']):
                            count_val = self.current_counts[f"error_{linear_idx}"]
                            for child in widget.children():
                                if isinstance(child, QLabel) and child.alignment() == Qt.AlignmentFlag.AlignCenter:
                                    child.setText(str(count_val))

                self.update_score()
                QMessageBox.information(self, "Resumed", "Record loaded successfully. You can continue checking.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to check database: {str(e)}")

    def save_record(self, is_final=False):
        doc, rde, rev = self._get_unique_key()
        
        if not doc:
            QMessageBox.warning(self, "Validation", "Please enter a Document Name.")
            return
            
        record = {
            "Document_Name": doc,
            "RDE_Name": rde,
            "Review_Number": int(rev)
        }
        
        for idx, error in enumerate(self.config_data['errors']):
            err_id = f"error_{idx}"
            record[f"Error_{idx+1}_({error['Error_Name']})"] = self.current_counts.get(err_id, 0)
            
        try:
            record["bonus_point"] = float(self.bonus_input.text())
        except:
            record["bonus_point"] = 0
            
        if is_final:
            record["total_points"] = float(self.score_display.text())
        else:
            record["total_points"] = "Pending"
            
        record["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save to Excel
        file_path = "Records.xlsx"
        df_new = pd.DataFrame([record])
        
        try:
            if os.path.exists(file_path):
                df = pd.read_excel(file_path)
                mask = (
                    (df['Document_Name'] == doc) & 
                    (df['RDE_Name'] == rde) & 
                    (df['Review_Number'].astype(str) == rev)
                )
                
                if mask.any():
                    # Overwrite existing row
                    idx_to_replace = df.index[mask][0]
                    for col in df_new.columns:
                        if col not in df.columns:
                            df[col] = pd.NA
                        df.at[idx_to_replace, col] = df_new.iloc[0][col]
                else:
                    # Append new row
                    df = pd.concat([df, df_new], ignore_index=True)
                    
                df.to_excel(file_path, index=False)
            else:
                df_new.to_excel(file_path, index=False)
                
            if is_final:
                QMessageBox.information(self, "Submitted", f"Record FINALIZED successfully!\nScore: {record['total_points']}")
                self.reset_form()
            else:
                QMessageBox.information(self, "Saved", "Record saved intermittently. Total score is pending.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save to Excel. Please ensure the file is closed.\nError: {str(e)}")

    def reset_form(self):
        self.doc_input.clear()
        self.bonus_input.setText("0")
        self.rev_input.setValue(1)
        
        for i in reversed(range(self.errors_layout.count())): 
            widget = self.errors_layout.itemAt(i).widget()
            if widget:
                for child in widget.children():
                    if isinstance(child, QLabel) and child.text().isdigit() and child.alignment() == Qt.AlignmentFlag.AlignCenter:
                        child.setText("0")
                        
        for key in self.current_counts:
            self.current_counts[key] = 0
            
        self.update_score()

def main():
    app = QApplication(sys.argv)
    font = QFont("Inter", 10)
    app.setFont(font)
    window = QualityRewardApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
