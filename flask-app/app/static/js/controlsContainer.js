// Controls container
const controls = document.createElement("div");
controls.className = "plot-controls";
const row1 = document.createElement("div");
row1.className = "widget-row";
const dimLabel = document.createElement("label");
dimLabel.textContent = "Dimension:";
const varLabel = document.createElement("label");
varLabel.textContent = "Variable:";
row1.appendChild(dimLabel);
row1.appendChild(dimSelect);
row1.appendChild(varLabel);
row1.appendChild(varSelect);

const row2 = document.createElement("div");
row2.className = "widget-row";
const timeLabel = document.createElement("label");
const levLabel = document.createElement("label");
row2.appendChild(timeLabel);
row2.appendChild(timeSlider);
row2.appendChild(levLabel);
row2.appendChild(levSlider);

controls.appendChild(row1);
controls.appendChild(row2);
