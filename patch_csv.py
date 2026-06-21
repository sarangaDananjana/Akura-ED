import os

file_path = r'c:\Users\Saranga\Desktop\Akura ED\templates\admin_panel\base.html'

with open(file_path, 'r', encoding='utf-8') as f:
    cont = f.read()

# Add inputs
inputs_html = """                      <div class="grid grid-cols-2 gap-4">
                          <div>
                              <label class="block text-sm font-semibold text-slate-700 mb-2">Start Row</label>
                              <input type="number" id="csvStartRow" value="1" required
                                  class="w-full border border-slate-200 rounded-xl px-4 py-3 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-indigo-500 transition-all outline-none">
                          </div>
                          <div>
                              <label class="block text-sm font-semibold text-slate-700 mb-2">End Row (-1 for all)</label>
                              <input type="number" id="csvEndRow" value="-1" required
                                  class="w-full border border-slate-200 rounded-xl px-4 py-3 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-indigo-500 transition-all outline-none">
                          </div>
                      </div>"""

if "csvStartRow" not in cont:
    cont = cont.replace(
        """                      <div>
                          <label class="block text-sm font-semibold text-slate-700 mb-2">CSV File</label>""",
        inputs_html + """\n                      <div>
                          <label class="block text-sm font-semibold text-slate-700 mb-2">CSV File</label>"""
    )

# Update Javascript
cont = cont.replace(
    "formData.append('file', document.getElementById('csvFile').files[0]);",
    "formData.append('start_row', document.getElementById('csvStartRow').value);\n            formData.append('end_row', document.getElementById('csvEndRow').value);\n            formData.append('file', document.getElementById('csvFile').files[0]);"
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(cont)
