def add_reading(self):
        """Add a new temperature reading to the data"""
        try:
            # Get data from input fields
            date_str = self.date_var.get()
            time_str = self.time_var.get()
            temp = self.temp_var.get()
            rating = self.rating_var.get()
            notes = self.notes_var.get()
            
            # Validate input data
            if not self.validate_input():
                return
            
            # Format date and time
            try:
                date_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                date_str = date_time.strftime("%Y-%m-%d")
                time_str = date_time.strftime("%H:%M:%S")
            except ValueError:
                messagebox.showerror("Error", "Invalid date or time format")
                return
            
            # Add to DataFrame
            new_row = pd.DataFrame({
                'Date': [date_str], 
                'Time': [time_str], 
                'Temperature': [temp], 
                'Rating': [rating],
                'Notes': [notes]
            })
            
            self.df = pd.concat([self.df, new_row], ignore_index=True)
            
            # Save data
            self.save_data()
            
            # Train models if enough data is available
            if len(self.df) >= 5:
                self.train_all_models()
            
            # Update display
            self.update_display()
            
            # Show success message
            messagebox.showinfo("Added Successfully", f"Reading added: {temp}°C - {rating}")
            
            # Clear fields for next input
            self.clear_input_fields(keep_date=True)
        except Exception as e:
            messagebox.showerror("Error", f"Error adding reading: {e}")
            print(f"Error adding reading: {e}")
    
    def clear_input_fields(self, keep_date=False):
        """Clear input fields"""
        if not keep_date:
            now = datetime.now()
            self.date_var.set(now.strftime("%Y-%m-%d"))
            self.time_var.set(now.strftime("%H:%M"))
        
        self.notes_var.set("")
        self.temp_var.set(25.0)
        self.rating_var.set("Normal")
    
    def set_current_datetime(self):
        """Set current date and time"""
        now = datetime.now()
        self.date_var.set(now.strftime("%Y-%m-%d"))
        self.time_var.set(now.strftime("%H:%M"))
    
    def delete_selected(self):
        """Delete selected reading from database"""
        selection = self.tree.selection()
        
        if not selection:
            messagebox.showinfo("Alert", "Please select a reading to delete")
            return
        
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected readings?")
        
        if confirm:
            try:
                for item in selection:
                    item_values = self.tree.item(item, "values")
                    date_str = item_values[0]
                    time_str = item_values[1]
                    
                    # Delete row from DataFrame
                    self.df = self.df[(self.df['Date'] != date_str) | (self.df['Time'] != time_str)]
                
                # Save data after deletion
                self.save_data()
                
                # Retrain models if enough data is available
                if len(self.df) >= 5:
                    self.train_all_models()
                
                # Update display
                self.update_display()
                
                messagebox.showinfo("Deleted", "Selected readings deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting readings: {e}")
                print(f"Error deleting readings: {e}")
    
    def on_tree_select(self, event):
        """Handle row selection event from table"""
        selection = self.tree.selection()
        
        if selection:
            # Get values of selected row
            item = selection[0]
            item_values = self.tree.item(item, "values")
            
            # Update input fields with selected values
            self.date_var.set(item_values[0])
            self.time_var.set(item_values[1])
            self.temp_var.set(float(item_values[2].replace('°C', '')))
            self.rating_var.set(item_values[3])
            
            if len(item_values) > 4:
                self.notes_var.set(item_values[4])
    
    def filter_data(self):
        """Filter data in table by search criteria"""
        search_text = self.search_var.get().lower()
        filter_value = self.filter_var.get()
        
        # Update table
        self.tree.delete(*self.tree.get_children())
        
        for i, row in self.df.iterrows():
            # Check for rating filter match
            rating_match = filter_value == "All" or row['Rating'] == filter_value
            
            # Check for search text match
            search_match = True
            if search_text:
                row_text = f"{row['Date']} {row['Time']} {row['Temperature']} {row['Rating']} {row.get('Notes', '')}"
                search_match = search_text in row_text.lower()
            
            # Add row if matches search criteria and filter
            if rating_match and search_match:
                self.tree.insert("", "end", values=(
                    row['Date'], 
                    row['Time'], 
                    f"{row['Temperature']:.1f}°C", 
                    row['Rating'],
                    row.get('Notes', '')
                ))
    
    def sort_treeview(self, tree, col, reverse):
        """Sort table by selected column"""
        # Get values from selected column
        data = [(tree.set(item, col), item) for item in tree.get_children('')]
        
        # Sort data
        data.sort(reverse=reverse)
        
        # Rearrange table items
        for i, (val, item) in enumerate(data):
            tree.move(item, '', i)
        
        # Toggle sort direction for next click
        tree.heading(col, command=lambda c=col: self.sort_treeview(tree, c, not reverse))
    
    def validate_input(self):
        """Validate input data"""
        try:
            # Validate date
            date_str = self.date_var.get()
            datetime.strptime(date_str, "%Y-%m-%d")
            
            # Validate time
            time_str = self.time_var.get()
            if ":" not in time_str:
                messagebox.showerror("Error", "Invalid time format. Use HH:MM format")
                return False
            
            # Validate temperature
            temp = self.temp_var.get()
            if temp < -50 or temp > 60:
                messagebox.showerror("Error", "Temperature out of valid range (-50 to 60 degrees Celsius)")
                return False
            
            return True
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD format")
            return False
    
    def update_display(self):
        """Update data display, statistics, and graphs"""
        # Update table
        self.filter_data()
        
        # Update readings count in status bar
        if not self.df.empty:
            self.records_var.set(f"Readings: {len(self.df)}")
        else:
            self.records_var.set("No readings")
        
        # Update statistics if data exists
        if not self.df.empty:
            self.avg_var.set(f"{self.df['Temperature'].mean():.1f}°C")
            self.max_var.set(f"{self.df['Temperature'].max():.1f}°C")
            self.min_var.set(f"{self.df['Temperature'].min():.1f}°C")
            self.std_var.set(f"{self.df['Temperature'].std():.2f}°C")
            
            # Update graph
            self.update_graph()
            
            # Update predictions if auto-predict is enabled
            if self.app_config["auto_predict"] and len(self.df) >= 5:
                self.update_prediction()
                self.update_extended_predictions()
        
        # Update status bar
        self.status_var.set(f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def update_graph(self):
        """Update graph based on current data and settings"""
        self.ax.clear()
        
        if len(self.df) > 0:
            # Apply period filtering
            filtered_df = self.filter_by_period(self.df.copy())
            
            if len(filtered_df) > 0:
                # Create numerical index for date/time
                filtered_df = filtered_df.sort_values(by=['Date', 'Time'])
                filtered_df['index'] = range(len(filtered_df))
                
                # Plot data based on selected plot type
                plot_type = self.plot_type_var.get()
                
                if plot_type == "Line":
                    self.ax.plot(filtered_df['index'], filtered_df['Temperature'], 'o-', color='#3498db', label='Temperature')
                elif plot_type == "Scatter":
                    self.ax.scatter(filtered_df['index'], filtered_df['Temperature'], color='#2ecc71', s=50, label='Temperature')
                elif plot_type == "Bar":
                    self.ax.bar(filtered_df['index'], filtered_df['Temperature'], color='#9b59b6', alpha=0.7, label='Temperature')
                
                # Add trend line if enough data is available
                if len(filtered_df) >= 3 and plot_type != "Bar":
                    x = np.array(filtered_df['index']).reshape(-1, 1)
                    y = np.array(filtered_df['Temperature'])
                    
                    x_line = np.linspace(min(x), max(x) + 5, 100).reshape(-1, 1)
                    
                    # Use active model for prediction
                    model = self.models[self.active_model]
                    
                    try:
                        if self.active_model == "linear":
                            model.fit(x, y)
                            y_line = model.predict(x_line)
                        else:
                            # Use polynomial features
                            poly = self.poly_features[self.active_model]
                            x_poly = poly.fit_transform(x)
                            model.fit(x_poly, y)
                            x_line_poly = poly.transform(x_line)
                            y_line = model.predict(x_line_poly)
                        
                        self.ax.plot(x_line, y_line, '--', color='#e74c3c', 
                                    label=f'Trend ({self.get_model_name(self.active_model)})')
                    except Exception as e:
                        print(f"Error plotting trend line: {e}")
                
                # Customize appearance
                self.ax.set_xlabel('Time Sequence')
                self.ax.set_ylabel('Temperature (°C)')
                self.ax.set_title('Temperature Changes Over Time')
                self.ax.grid(True, linestyle='--', alpha=0.7)
                self.ax.legend()
                
                # Display dates for x-axis
                if len(filtered_df) > 10:
                    step = len(filtered_df) // 5
                    ticks_loc = filtered_df['index'][::step].tolist()
                    ticks_labels = filtered_df['Date'][::step].tolist()
                    self.ax.set_xticks(ticks_loc)
                    self.ax.set_xticklabels(ticks_labels, rotation=45)
                else:
                    self.ax.set_xticks(filtered_df['index'])
                    self.ax.set_xticklabels(filtered_df['Date'], rotation=45)
                
                # Add rating as different colors if plot type is scatter
                if plot_type == "Scatter":
                    colors = {'Very Cold': '#3498db', 'Cold': '#87cefa', 'Normal': '#2ecc71', 'Warm': '#f39c12', 'Very Hot': '#e74c3c'}
                    for rating in colors.keys():
                        mask = filtered_df['Rating'] == rating
                        if mask.any():
                            self.ax.scatter(filtered_df.loc[mask, 'index'], filtered_df.loc[mask, 'Temperature'], 
                                        color=colors[rating], s=50, label=f'Rating: {rating}')
        
        # Update plot
        self.fig.tight_layout()
        self.canvas.draw()
    
    def filter_by_period(self, df):
        """Filter data by selected time period"""
        period = self.period_var.get()
        
        if period == "All" or df.empty:
            return df
        
        # Convert date column to datetime type
        df['datetime'] = pd.to_datetime(df['Date'])
        
        # Determine start date based on selected period
        now = datetime.now()
        
        if period == "Last 7 Days":
            start_date = now - timedelta(days=7)
        elif period == "Last 30 Days":
            start_date = now - timedelta(days=30)
        elif period == "Last 90 Days":
            start_date = now - timedelta(days=90)
        
        # Filter data
        filtered_df = df[df['datetime'] >= start_date]
        
        # Remove temporary column
        filtered_df = filtered_df.drop(columns=['datetime'])
        
        return filtered_df
    
    def train_all_models(self):
        """Train all prediction models using available data"""
        try:
            if len(self.df) >= 5:
                # Convert data to suitable format for training
                x = np.array(range(len(self.df))).reshape(-1, 1)
                y = np.array(self.df['Temperature'])
                
                # Train linear model
                self.models["linear"].fit(x, y)
                
                # Train polynomial models
                for model_name in ["poly2", "poly3"]:
                    poly = self.poly_features[model_name]
                    x_poly = poly.fit_transform(x)
                    self.models[model_name].fit(x_poly, y)
                
                # Save models
                for model_name, model in self.models.items():
                    model_path = os.path.join(self.app_config["data_dir"], f"{model_name}_model.pkl")
                    joblib.dump(model, model_path)
                
                # Evaluate models accuracy and determine best model
                self.evaluate_models(x, y)
                
                print("All models trained and saved successfully")
                self.status_var.set("Models trained successfully")
            else:
                messagebox.showinfo("Alert", "At least 5 readings required for accurate prediction")
                self.status_var.set("Insufficient readings for training")
        except Exception as e:
            print(f"Error training models: {e}")
            self.status_var.set(f"Error training models")
    
    def evaluate_models(self, x, y):
        """Evaluate model performance and select the best one"""
        best_score = -1
        best_model = None
        
        # Calculate accuracy for each model
        scores = {}
        
        # Evaluate linear model
        y_pred = self.models["linear"].predict(x)
        r2 = r2_score(y, y_pred)
        scores["linear"] = r2
        
        # Evaluate polynomial models
        for model_name in ["poly2", "poly3"]:
            poly = self.poly_features[model_name]
            x_poly = poly.transform(x)
            y_pred = self.models[model_name].predict(x_poly)
            r2 = r2_score(y, y_pred)
            scores[model_name] = r2
        
        # Determine best model
        for model_name, score in scores.items():
            if score > best_score:
                best_score = score
                best_model = model_name
        
        # Update active model and statistics
        if best_model:
            self.active_model = best_model
            self.model_var.set(best_model)
            self.r2_var.set(f"{best_score:.4f}")
            print(f"Best model: {best_model} with accuracy {best_score:.4f}")
    
    def update_prediction(self):
        """Update temperature prediction for next reading"""
        try:
            if len(self.df) >= 5:
                # Predict next reading using active model
                next_idx = len(self.df)
                next_x = np.array([[next_idx]])
                
                model = self.models[self.active_model]
                
                if self.active_model == "linear":
                    pred = model.predict(next_x)[0]
                else:
                    poly = self.poly_features[self.active_model]
                    next_x_poly = poly.transform(next_x)
                    pred = model.predict(next_x_poly)[0]
                
                # Update prediction display
                self.pred_var.set(f"{pred:.1f}°C")
                
                return pred
            else:
                self.pred_var.set("-- °C")
                messagebox.showinfo("Alert", "At least 5 readings required for accurate prediction")
                return None
        except Exception as e:
            messagebox.showerror("Error", f"Error during prediction: {e}")
            print(f"Prediction error: {e}")
            return None
    
    def update_extended_predictions(self):
        """Update future predictions for multiple days"""
        try:
            # Update days value in settings
            days = self.days_var.get()
            self.app_config["prediction_days"] = days
            self.save_config()
            
            # Clear table
            self.pred_tree.delete(*self.pred_tree.get_children())
            
            if len(self.df) < 5:
                messagebox.showinfo("Alert", "At least 5 readings required for accurate prediction")
                return
            
            # Get last date in data
            last_date = pd.to_datetime(self.df['Date'].iloc[-1])
            
            model = self.models[self.active_model]
            
            # Predict for each day
            for i in range(1, days + 1):
                next_idx = len(self.df) + i - 1
                next_x = np.array([[next_idx]])
                
                # Predict using appropriate model
                if self.active_model == "linear":
                    pred = model.predict(next_x)[0]
                else:
                    poly = self.poly_features[self.active_model]
                    next_x_poly = poly.transform(next_x)
                    pred = model.predict(next_x_poly)[0]
                
                # Calculate date
                pred_date = last_date + timedelta(days=i)
                date_str = pred_date.strftime("%Y-%m-%d")
                
                # Calculate confidence (simplified)
                confidence = max(0, 1 - (i * 0.05))
                
                # Add to predictions table
                self.pred_tree.insert("", "end", values=(
                    date_str,
                    f"{pred:.1f}°C",
                    f"{confidence:.0%}"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error during prediction: {e}")
            print(f"Error in future predictions: {e}")
    
    def change_model(self):
        """Change active model used for prediction"""
        self.active_model = self.model_var.get()
        print(f"Active model changed to: {self.active_model}")
        
        # Update display and predictions
        self.update_graph()
        self.update_prediction()
        self.update_extended_predictions()
    
    def get_model_name(self, model_key):
        """Get descriptive name for model"""
        models_names = {
            "linear": "Linear",
            "poly2": "Polynomial Degree 2",
            "poly3": "Polynomial Degree 3"
        }
        return models_names.get(model_key, model_key)
    
    def save_data(self):
        """Save data to CSV file"""
        try:
            # Ensure directory exists
            if not os.path.exists(self.app_config["data_dir"]):
                os.makedirs(self.app_config["data_dir"])
            
            # Save data
            path = os.path.join(self.app_config["data_dir"], self.app_config["history_file"])
            self.df.to_csv(path, index=False)
            print("Data saved successfully")
        except Exception as e:
            print(f"Error saving data: {e}")
            messagebox.showerror("Error", f"Error saving data: {e}")
    
    def export_data(self):
        """Export data to CSV file"""
        if self.df.empty:
            messagebox.showinfo("Alert", "No data to export")
            return
        
        try:
            # Ask user for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Data"
            )
            
            if file_path:
                self.df.to_csv(file_path, index=False)
                messagebox.showinfo("Export Complete", f"Data exported successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting data: {e}")
    
    def import_data(self):
        """Import data from CSV file"""
        try:
            # Ask user for file location
            file_path = filedialog.askopenfilename(
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Import Data"
            )
            
            if file_path:
                # Check file format
                imported_df = pd.read_csv(file_path)
                
                # Check for required columns
                required_columns = ['Date', 'Time', 'Temperature', 'Rating']
                if not all(col in imported_df.columns for col in required_columns):
                    messagebox.showerror("Error", "Imported file does not contain required columns")
                    return
                
                # Ask user about import method
                response = messagebox.askyesno("Confirm Import", 
                                              "Do you want to replace current data?\n(Choose 'No' to merge data)")
                
                if response:
                    # Replace data
                    self.df = imported_df
                else:
                    # Merge data
                    self.df = pd.concat([self.df, imported_df], ignore_index=True)
                    
                    # Remove potential duplicates
                    self.df = self.df.drop_duplicates(subset=['Date', 'Time'], keep='last')
                
                # Save imported data
                self.save_data()
                
                # Retrain models
                if len(self.df) >= 5:
                    self.train_all_models()
                
                # Update display
                self.update_display()
                
                messagebox.showinfo("Import Complete", f"Successfully imported {len(imported_df)} readings")
        except Exception as e:
            messagebox.showerror("Error", f"Error importing data: {e}")
    
    def reset_system(self):
        """Reset system and delete all stored data"""
        confirm = messagebox.askyesno("Confirm Reset", 
                                    "Are you sure you want to reset the system?\n"
                                    "All data and trained models will be deleted.\n"
                                    "This action cannot be undone!")
        
        if confirm:
            try:
                # Reset data
                self.df = pd.DataFrame(self.temp_data)
                
                # Reset models
                self.models = {
                    "linear": LinearRegression(),
                    "poly2": LinearRegression(),
                    "poly3": LinearRegression()
                }
                
                # Delete stored files
                for file_name in os.listdir(self.app_config["data_dir"]):
                    if file_name.endswith(".csv") or file_name.endswith(".pkl"):
                        os.remove(os.path.join(self.app_config["data_dir"], file_name))
                
                # Update display
                self.update_display()
                
                # Clear input fields
                self.clear_input_fields()
                
                messagebox.showinfo("Reset Complete", "System reset successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Error resetting system: {e}")
    
    def show_about(self):
        """Display information about the application"""
        about_text = """AI-Powered Temperature Monitoring System
Version 2.0

Advanced system for recording, monitoring, and analyzing temperature readings
with prediction capabilities using AI algorithms.

Key Features:
• Record temperature readings with date and time
• Classify readings and add notes
• Advanced statistical analysis
• Interactive graphs
• Future predictions using multiple models
• Import and export data

© All Rights Reserved 2025"""
        
        messagebox.showinfo("About", about_text)
    
    def show_help(self):
        """Display user manual"""
        help_text = """Temperature Monitoring System User Guide

How to Add a New Reading:
1. Enter date and time (or use "Now" button)
2. Enter temperature
3. Select appropriate rating
4. Add notes (optional)
5. Click "Add Reading" button

How to View and Analyze Data:
• Use "Time Period" menu to focus on specific period
• Change graph type as needed
• Select prediction model from "Prediction Model" menu
• Use search and filter tools to find specific readings

Helpful Tips:
• Export data regularly for backup
• System needs at least 5 readings for accurate prediction
• More data leads to more accurate predictions
• Use "Update Data" button if changes don't appear automatically"""
        
        messagebox.showinfo("User Guide", help_text)


if __name__ == "__main__":
    root = tk.Tk()
    # Configure general style
    style = ttk.Style()
    style.configure("TSpinbox", arrowsize=15)
    
    app = TempMonitorSystem(root)
    root.mainloop()