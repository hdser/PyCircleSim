import panel as pn
import param
import duckdb
import pandas as pd
import holoviews as hv
from pathlib import Path

pn.extension('tabulator')
hv.extension('bokeh')

# Optional CSS for a dark "terminal-like" SQL editor
custom_css = """
.custom-sql-input .bk-input {
    background-color: #2e3440 !important;
    color: #d8dee9 !important;
    font-family: monospace !important;
    font-size: 12px !important;
}
"""
pn.extension(raw_css=[custom_css])


# =============================================================================
# PLOT CONFIG CLASSES
# =============================================================================

class LinePlotConfig(param.Parameterized):
    """Line Plot config with multiple Y columns, optional group_col, etc."""
    df = param.DataFrame()

    x_col     = param.ObjectSelector()
    y_cols    = param.ListSelector(default=[])
    group_col = param.ObjectSelector(default=None, allow_None=True)

    def __init__(self, df, **params):
        super().__init__(**params)
        self.df = df.reset_index(drop=True)
        cols = list(self.df.columns)
        self.param.x_col.objects     = cols
        self.param.y_cols.objects    = cols
        self.param.group_col.objects = [None] + cols

        if cols:
            self.x_col = cols[0]
        if len(cols) > 1:
            self.y_cols = [cols[1]]

    @param.depends('x_col', 'y_cols', 'group_col')
    def view(self):
        df = self.df
        if df.empty:
            return pn.pane.Markdown("No data to plot (empty).")

        if self.x_col not in df.columns:
            return pn.pane.Markdown("Please choose a valid X column.")
        if not self.y_cols:
            return pn.pane.Markdown("Please select at least one Y column.")

        # Validate that all y_cols are numeric
        for y in self.y_cols:
            if y not in df.columns:
                return pn.pane.Markdown(f"Invalid Y col: {y}")
            if not pd.api.types.is_numeric_dtype(df[y]):
                return pn.pane.Markdown(
                    f"Column '{y}' is not numeric. A line plot requires numeric Y columns."
                )

        import hvplot.pandas
        overlays = []
        for y in self.y_cols:
            # If group_col => grouped lines
            if self.group_col and self.group_col in df.columns:
                grp_line = df.hvplot.line(
                    x=self.x_col, y=y, by=self.group_col,
                    width=1000, height=500
                )
                overlays.append(grp_line)
            else:
                curve = hv.Curve(df, self.x_col, y).opts(width=1000, height=500)
                overlays.append(curve)

        if not overlays:
            return pn.pane.Markdown("No valid lines to display.")
        combined = overlays[0]
        for o in overlays[1:]:
            combined *= o
        return pn.pane.HoloViews(combined)


class BarPlotConfig(param.Parameterized):
    """
    Bar Plot config:
      - Orientation (vertical or horizontal)
      - multiple Y columns, optional group_col
      - stacked vs grouped bar_mode
      - can handle text Y by grouping counts
    """
    df = param.DataFrame()

    x_col     = param.ObjectSelector()
    y_cols    = param.ListSelector(default=[])
    group_col = param.ObjectSelector(default=None, allow_None=True)
    bar_mode  = param.ObjectSelector(default='grouped', objects=['grouped', 'stacked'])
    orientation = param.ObjectSelector(default='vertical', objects=['vertical', 'horizontal'])

    def __init__(self, df, **params):
        super().__init__(**params)
        self.df = df.reset_index(drop=True)
        cols = list(self.df.columns)

        self.param.x_col.objects     = cols
        self.param.y_cols.objects    = cols
        self.param.group_col.objects = [None] + cols

        if cols:
            self.x_col = cols[0]
        if len(cols) > 1:
            self.y_cols = [cols[1]]

    @param.depends('x_col', 'y_cols', 'group_col', 'bar_mode', 'orientation')
    def view(self):
        import hvplot.pandas

        df = self.df
        if df.empty:
            return pn.pane.Markdown("No data to plot (empty).")

        if self.x_col not in df.columns:
            return pn.pane.Markdown("Please select a valid X column.")
        if not self.y_cols:
            return pn.pane.Markdown("Please select at least one Y column.")

        is_horizontal = (self.orientation == 'horizontal')
        overlays = []
        for y in self.y_cols:
            if y not in df.columns:
                return pn.pane.Markdown(f"Invalid Y column: {y}")

            # If Y is numeric => direct bar
            if pd.api.types.is_numeric_dtype(df[y]):
                chart = df.hvplot.bar(
                    x=self.x_col, y=y,
                    stacked=(self.bar_mode == 'stacked'),
                    by=self.group_col if self.group_col else None,
                    rot=(45 if not is_horizontal else 0),  # rotate labels for clarity
                    width=1000, height=500
                )
                if is_horizontal:
                    chart = chart.opts(invert_axes=True)
                overlays.append(chart)
            else:
                # Y is textual => aggregator approach
                # groupby [x_col, y] => size => "Count"
                temp = df.groupby([self.x_col, y]).size().reset_index(name='Count')
                chart = temp.hvplot.bar(
                    x=self.x_col, y='Count',
                    stacked=(self.bar_mode == 'stacked'),
                    by=y,  # treat 'y' as grouping
                    rot=(45 if not is_horizontal else 0),
                    width=1000, height=500
                )
                if is_horizontal:
                    chart = chart.opts(invert_axes=True)
                overlays.append(chart)

        if not overlays:
            return pn.pane.Markdown("No bar data.")
        combined = overlays[0]
        for o in overlays[1:]:
            combined *= o
        return pn.pane.HoloViews(combined)


class ScatterPlotConfig(param.Parameterized):
    """
    Scatter Plot config: multiple Y columns, color_col, size_col.
    """
    df = param.DataFrame()

    x_col     = param.ObjectSelector()
    y_cols    = param.ListSelector(default=[])
    color_col = param.ObjectSelector(default=None, allow_None=True)
    size_col  = param.ObjectSelector(default=None, allow_None=True)

    def __init__(self, df, **params):
        super().__init__(**params)
        self.df = df.reset_index(drop=True)
        cols = list(self.df.columns)

        self.param.x_col.objects     = cols
        self.param.y_cols.objects    = cols
        self.param.color_col.objects = [None] + cols
        self.param.size_col.objects  = [None] + cols

        if cols:
            self.x_col = cols[0]
        if len(cols) > 1:
            self.y_cols = [cols[1]]

    @param.depends('x_col', 'y_cols', 'color_col', 'size_col')
    def view(self):
        df = self.df
        if df.empty:
            return pn.pane.Markdown("No data to plot (empty).")

        if self.x_col not in df.columns:
            return pn.pane.Markdown("Please choose a valid X column.")
        if not self.y_cols:
            return pn.pane.Markdown("Please select at least one Y column.")

        import hvplot.pandas
        overlays = []
        for y in self.y_cols:
            if y not in df.columns:
                return pn.pane.Markdown(f"Invalid Y column: {y}")
            if not pd.api.types.is_numeric_dtype(df[y]):
                return pn.pane.Markdown(
                    f"Column '{y}' is not numeric. Scatter requires numeric Y columns."
                )

            if self.color_col and self.color_col in df.columns:
                sc = df.hvplot.scatter(
                    x=self.x_col, y=y, by=self.color_col,
                    width=1000, height=500
                )
                overlays.append(sc)
            else:
                scatter = hv.Scatter(df, self.x_col, y).opts(width=1000, height=500)
                if self.size_col and self.size_col in df.columns:
                    sizes = df[self.size_col]
                    if pd.api.types.is_numeric_dtype(sizes):
                        smin, smax = sizes.min(), sizes.max()
                        rng = smax - smin if smax != smin else 1
                        scaled = 5 + 15*(sizes - smin)/rng
                        scatter = scatter.opts(size=scaled.tolist())
                overlays.append(scatter)

        if not overlays:
            return pn.pane.Markdown("No scatter data.")
        combined = overlays[0]
        for o in overlays[1:]:
            combined *= o
        return pn.pane.HoloViews(combined)


class NetworkPlotConfig(param.Parameterized):
    """Network Graph config: from_col, to_col."""
    df = param.DataFrame()
    from_col = param.ObjectSelector(default=None, allow_None=True)
    to_col   = param.ObjectSelector(default=None, allow_None=True)

    def __init__(self, df, **params):
        super().__init__(**params)
        self.df = df.reset_index(drop=True)
        cols = list(self.df.columns)
        self.param.from_col.objects = [None] + cols
        self.param.to_col.objects   = [None] + cols

        if 'from' in cols:
            self.from_col = 'from'
        if 'to' in cols:
            self.to_col = 'to'

    @param.depends('from_col', 'to_col')
    def view(self):
        df = self.df
        if df.empty:
            return pn.pane.Markdown("No data for network graph.")
        if not self.from_col or not self.to_col:
            return pn.pane.Markdown("Select valid from_col and to_col.")
        if self.from_col not in df.columns or self.to_col not in df.columns:
            return pn.pane.Markdown("Invalid from/to columns.")

        edges = [(row[self.from_col], row[self.to_col]) for _, row in df.iterrows()]
        try:
            graph = hv.Graph(edges)
            return pn.pane.HoloViews(graph.opts(width=1000, height=500))
        except Exception as e:
            return pn.pane.Markdown(f"Network Graph error: {e}")


def build_plot_config(plot_type, df):
    """Factory for the correct Param-based config object."""
    if plot_type == 'Line Plot':
        return LinePlotConfig(df)
    elif plot_type == 'Bar Plot':
        return BarPlotConfig(df)
    elif plot_type == 'Scatter Plot':
        return ScatterPlotConfig(df)
    elif plot_type == 'Network Graph':
        return NetworkPlotConfig(df)
    else:
        raise ValueError(f"Unknown plot type: {plot_type}")


# =============================================================================
# Main Explorer App
# =============================================================================
class DatabaseExplorer(param.Parameterized):
    """
    A Panel-based application for:
      - Running a SQL query => showing a small, non-editable table with horizontal scroll
      - Clicking "+" => choose a plot type => new tab with the relevant config
      - Plots at 1000x500 for extra width
      - Bar plots have orientation toggle, can handle text Y columns
    """
    sql_query = param.String(default='')
    current_query = param.String(default='')

    def __init__(self, db_path):
        super().__init__()
        self.conn = duckdb.connect(db_path, read_only=True)

        # Gather table & schema info
        self.tables = self._get_tables()
        self.schemas = self._get_schemas()

        # Load .sql queries
        self.queries = self._load_queries()

        self.current_df = pd.DataFrame()
        self.create_layout()

    # ---------------------------------------------------------------------
    # DB queries
    # ---------------------------------------------------------------------
    def _load_queries(self):
        queries = {'Custom Query': None}
        qdir = Path(__file__).parent / 'queries'
        if not qdir.exists():
            return queries

        for sub in qdir.iterdir():
            if sub.is_dir():
                cat_name = sub.name.replace('_', ' ').title()
                for sql_file in sub.glob('*.sql'):
                    try:
                        qname = f"{cat_name}: {sql_file.stem.replace('_', ' ').title()}"
                        queries[qname] = sql_file.read_text()
                    except Exception as e:
                        print(f"Error reading {sql_file}: {e}")
        return queries

    def _get_tables(self):
        rows = self.conn.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='main'"
        ).fetchall()
        return sorted([r[0] for r in rows])

    def _get_schemas(self):
        schemas = {}
        for tbl in self.tables:
            try:
                df_schema = self.conn.execute(f"DESCRIBE {tbl}").df()
                short = pd.DataFrame({
                    'Column': df_schema['column_name'],
                    'Type': df_schema['column_type']
                }).reset_index(drop=True)
                schemas[tbl] = short
            except Exception as e:
                print(f"Error describing {tbl}: {e}")
                schemas[tbl] = pd.DataFrame(columns=['Column', 'Type'])
        return schemas

    # ---------------------------------------------------------------------
    # Query => Main table
    # ---------------------------------------------------------------------
    def _execute_query(self, event=None):
        try:
            self.error_display.object = ""
            self.current_query = self.query_editor.value
            df = self.conn.execute(self.current_query).df()
            self.current_df = df
            self._update_main_table()
        except Exception as e:
            self.error_display.object = f"Error: {e}"
            self.main_result_container.objects = [pn.pane.Markdown("Query execution failed.")]


    def _format_json_columns(self, df):
        """Format JSON columns for better display, with both compact and full versions"""
        import json
        
        df = df.copy()
        for col in df.columns:
            # Check if column contains JSON data
            if df[col].dtype == 'object':
                try:
                    # Test if first non-null value is JSON
                    first_valid = df[col].dropna().iloc[0] if not df[col].empty else None
                    if isinstance(first_valid, str) and isinstance(json.loads(first_valid), (dict, list)):
                        # Create HTML formatted version with expand/collapse
                        df[col] = df[col].apply(lambda x: 
                            self._create_expandable_json(x, col) if pd.notna(x) else x
                        )
                except (ValueError, json.JSONDecodeError, IndexError):
                    continue
        return df

    def _create_expandable_json(self, json_str, col_name):
        """Create HTML for expandable JSON content"""
        import json
        
        try:
            # Parse and format the JSON
            parsed = json.loads(json_str)
            compact = json.dumps(parsed)[:80] + "..." if len(json_str) > 80 else json_str
            formatted = json.dumps(parsed, indent=2)
            
            # Create HTML with expand/collapse functionality
            html = f'''
            <div class="json-container" style="position: relative; min-height: 20px;">
                <div class="compact-view" style="cursor: pointer;" 
                     onclick="this.style.display='none'; this.nextElementSibling.style.display='block'; this.closest('.tabulator-cell').style.height = 'auto'; this.closest('.tabulator-row').style.height = 'auto'; this.closest('.tabulator-row').style.minHeight = '300px';">
                    {compact}
                </div>
                <div class="expanded-view" style="display: none; position: relative; width: 100%;">
                    <pre style="background-color: white; color: black; padding: 10px; border-radius: 4px; margin: 0; max-height: 400px; overflow-y: auto; border: 1px solid #ddd; width: 100%; box-sizing: border-box;">
{formatted}
                    </pre>
                    <button onclick="this.parentElement.style.display='none'; this.parentElement.previousElementSibling.style.display='block'; this.closest('.tabulator-row').style.height = ''; this.closest('.tabulator-row').style.minHeight = '';"
                            style="position: absolute; top: 5px; right: 5px; padding: 2px 6px; background: white; color: black; border: 1px solid #ddd; border-radius: 3px; cursor: pointer;">
                        Collapse
                    </button>
                </div>
            </div>
            '''
            return html
        except:
            return json_str

    def _update_main_table(self):
        if self.current_df.empty:
            self.main_result_container.objects = [
                pn.pane.Markdown("No data or empty DataFrame.")
            ]
            return

        # Format JSON columns before display
        formatted_df = self._format_json_columns(self.current_df)
        
        # Configure formatters
        formatters = {}
        for col in formatted_df.columns:
            sample = formatted_df[col].iloc[0] if not formatted_df.empty else ""
            if isinstance(sample, str) and sample.strip().startswith('<div class="json-container"'):
                formatters[col] = {'type': 'html'}
            else:
                formatters[col] = {'type': 'text'}

        # Create Tabulator
        tab = pn.widgets.Tabulator(
            formatted_df.reset_index(drop=True),
            pagination='remote',
            page_size=10,
            show_index=False,
            disabled=True,
            layout='fit_data_fill',
            theme='default',
            formatters=formatters,
            stylesheets=[
                # General table styling
                ":host .tabulator {font-size: 12px; width: 100% !important;}",
                ":host .tabulator-tableholder {overflow-x: auto !important;}",
                
                # Remove alternating colors and hover effects
                ".tabulator-table .tabulator-row {background-color: transparent !important;}",
                ".tabulator-table .tabulator-row.tabulator-row-even {background-color: transparent !important;}",
                #".tabulator-row:hover {background: transparent !important;}",
                #".tabulator-row.tabulator-selectable:hover {background: transparent !important;}",
                # Keep text color consistent on hover
                ".tabulator-row:hover .tabulator-cell {color: #073d8c !important;}",
                ".tabulator-row.tabulator-selectable:hover .tabulator-cell {color: #073d8c !important;}",

                # Row & cell styling for wrapped text
                ":host .tabulator-row .tabulator-cell {"
                "    height: auto !important;"
                "    overflow: visible !important;"
                "    white-space: normal !important;"
                "    padding: 8px !important;"
                "}",
                ":host .tabulator-row {height: auto !important; min-height: 30px !important; color: black !important;}",
                ":host .tabulator-cell-content {"
                "    height: auto !important;"
                "    white-space: normal !important;"
                "    word-wrap: break-word !important;"
                "}",

                # Header styling
                ":host .tabulator-header .tabulator-col {background-color: #f8f9fa !important;}",
                ":host .tabulator-header .tabulator-col-content {white-space: nowrap !important; padding: 8px !important;}",

                # Ensure JSON remains visible when row is selected
                ":host .tabulator-row.tabulator-selected .json-container {color: black !important;}",
                ":host .tabulator-row.tabulator-selected .expanded-view {color: black !important; background-color: white !important;}",
                ":host .tabulator-row.tabulator-selected .compact-view {color: black !important;}",
            ],
            configuration={
                "maxHeight": "800px",
                "layout": "fitDataFill",
                "resizableRows": True,
                "resizableColumns": True,
                "selectable": True,
                "placeholder": "No Data Available",
                "data": formatted_df.to_dict('records'),
                "globalFilter": True,
                # Expand row on selection
                "rowSelected": """
                    function(row) {
                        row.getElement().style.height = 'auto';
                        var cells = row.getCells();
                        cells.forEach(function(cell) {
                            cell.getElement().style.whiteSpace = 'normal';
                        });
                    }
                """,
                "rowDeselected": """
                    function(row) {
                        row.getElement().style.height = '';
                        var cells = row.getCells();
                        cells.forEach(function(cell) {
                            cell.getElement().style.whiteSpace = '';
                        });
                    }
                """,
            },
            sizing_mode='stretch_width'
        )

        # Display the table
        self.main_result_container.objects = [
            tab
        ]

    # ---------------------------------------------------------------------
    # Plot creation => new tabs
    # ---------------------------------------------------------------------
    def _show_plot_type_selector(self, event=None):
        # A popup with a select + "Create Plot" button
        plot_type_select = pn.widgets.Select(
            name="Select Plot Type",
            options=[
                'Line Plot',
                'Bar Plot',
                'Scatter Plot',
                'Network Graph'
            ],
            width=180
        )
        confirm_btn = pn.widgets.Button(name="Create Plot", button_type="primary")

        dialog = pn.Column(
            pn.pane.Markdown("### Choose Plot Type"),
            plot_type_select,
            confirm_btn,
            sizing_mode='fixed',
            width=220,
            height=160,
        )

        # Position near the plus button
        self.overlay_popup.clear()
        self.overlay_popup.style = {
            'position': 'absolute',
            'right': '60px',
            'top': '40px',
            'z-index': '9999',
            'background-color': '#f8f8f8',
            'padding': '8px',
            'border': '1px solid #ccc',
            'border-radius': '4px'
        }
        self.overlay_popup[:] = [dialog]

        def _on_confirm(_):
            self.overlay_popup.clear()
            self._create_plot_tab(plot_type_select.value)

        confirm_btn.on_click(_on_confirm)

    def _create_plot_tab(self, chosen_plot_type):
        if self.current_df.empty:
            self.error_display.object = "No data available. Please run a query first."
            return

        config_obj = build_plot_config(chosen_plot_type, self.current_df)
        # Param panel depends on which config object we have
        if isinstance(config_obj, LinePlotConfig):
            parameters = ['x_col', 'y_cols', 'group_col']
            widgets_map = {
                'x_col':    {'type': pn.widgets.Select, 'width':150},
                'y_cols':   {'type': pn.widgets.MultiChoice, 'height':100, 'width':150},
                'group_col':{'type': pn.widgets.Select, 'width':150},
            }
        elif isinstance(config_obj, BarPlotConfig):
            parameters = ['x_col', 'y_cols', 'group_col', 'bar_mode', 'orientation']
            widgets_map = {
                'x_col':       {'type': pn.widgets.Select, 'width':150},
                'y_cols':      {'type': pn.widgets.MultiChoice, 'height':100, 'width':150},
                'group_col':   {'type': pn.widgets.Select, 'width':150},
                'bar_mode':    {'type': pn.widgets.Select, 'width':130},
                'orientation': {'type': pn.widgets.Select, 'width':130},
            }
        elif isinstance(config_obj, ScatterPlotConfig):
            parameters = ['x_col', 'y_cols', 'color_col', 'size_col']
            widgets_map = {
                'x_col':     {'type': pn.widgets.Select, 'width':150},
                'y_cols':    {'type': pn.widgets.MultiChoice, 'height':100, 'width':150},
                'color_col': {'type': pn.widgets.Select, 'width':150},
                'size_col':  {'type': pn.widgets.Select, 'width':150},
            }
        elif isinstance(config_obj, NetworkPlotConfig):
            parameters = ['from_col', 'to_col']
            widgets_map = {
                'from_col': {'type': pn.widgets.Select, 'width':150},
                'to_col':   {'type': pn.widgets.Select, 'width':150},
            }
        else:
            # fallback
            parameters = []
            widgets_map = {}

        config_panel = pn.Param(
            config_obj,
            parameters=parameters,
            show_name=False,
            sizing_mode='stretch_width',
            widgets=widgets_map
        )

        tab_content = pn.Row(
            config_obj.view,
            config_panel,
            sizing_mode='stretch_both'
        )

        idx = len(self.results_tabs)
        self.results_tabs.append((f"Plot {idx+1}", tab_content))

    # ---------------------------------------------------------------------
    # Layout
    # ---------------------------------------------------------------------
    def create_layout(self):
        # Sidebar
        table_selector = pn.widgets.Select(
            name='Select Table',
            options=self.tables,
            sizing_mode='stretch_width'
        )

        schema_viewer = pn.widgets.Tabulator(
            pd.DataFrame(),
            page_size=100,
            sizing_mode='stretch_width',
            show_index=False,
            disabled=True,
            layout='fit_data_stretch',
            theme='bootstrap5', 
            stylesheets=[":host .tabulator {font-size: 12px;}"],
            header_align={'Column': 'left', 'Type': 'right'},
            text_align={'Column': 'left', 'Type': 'right'}
        )

        def update_schema(evt):
            tbl = evt.new
            if tbl in self.schemas:
                sc = self.schemas[tbl].copy()
                sc.reset_index(drop=True, inplace=True)
                schema_viewer.value = sc
        table_selector.param.watch(update_schema, 'value')

        template_select = pn.widgets.Select(
            name='Available Queries',
            options=list(self.queries.keys()),
            value='Custom Query',
            sizing_mode='stretch_width'
        )

        def update_template(evt):
            q_name = evt.new
            if q_name in self.queries and self.queries[q_name] is not None:
                self.query_editor.value = self.queries[q_name]
        template_select.param.watch(update_template, 'value')

        sidebar_content = pn.Column(
            pn.pane.Markdown("### Database Tables"),
            table_selector,
            pn.layout.Divider(),
            pn.pane.Markdown("### Schema"),
            schema_viewer,
            pn.layout.Divider(),
            pn.pane.Markdown("### Query Templates"),
            template_select,
            sizing_mode='stretch_width',
        )

        # Main area
        self.query_editor = pn.widgets.TextAreaInput(
            value=self.sql_query,
            height=180,
            sizing_mode='stretch_width',
            css_classes=["custom-sql-input"],
            placeholder="Write your SQL here..."
        )
        self.execute_button = pn.widgets.Button(
            name='Execute Query',
            button_type='primary',
            width=120
        )
        self.execute_button.on_click(self._execute_query)

        sql_container = pn.Column(
            pn.pane.Markdown("### SQL Query"),
            self.query_editor,
            pn.layout.Divider(),
            self.execute_button,
            sizing_mode='stretch_width'
        )

        self.error_display = pn.pane.Markdown("")

        self.main_result_container = pn.Column(
            pn.pane.Markdown("Execute a query to see results."),
            sizing_mode='stretch_width'
        )
        main_result_accordion = pn.Accordion(
            ("Main Result", self.main_result_container),
            active=[],
            sizing_mode='stretch_width'
        )

        # Additional Plots
        self.results_tabs = pn.Tabs(tabs_location='above', closable=True)

        add_tab_button = pn.widgets.Button(name="+", button_type="success", width=30)
        add_tab_button.on_click(self._show_plot_type_selector)

        # Overlay popup container for the plot-type selection
        self.overlay_popup = pn.Column()

        tabs_row = pn.Row(
            self.results_tabs,
            pn.Spacer(),
            self.overlay_popup,
            add_tab_button,
            sizing_mode='stretch_width'
        )

        additional_views = pn.Column(
            pn.pane.Markdown("### Additional Views"),
            tabs_row,
            sizing_mode='stretch_both'
        )

        main_content = pn.Column(
            sql_container,
            pn.layout.Divider(),
            self.error_display,
            main_result_accordion,
            pn.layout.Divider(),
            additional_views,
            sizing_mode='stretch_both'
        )

        template = pn.template.MaterialTemplate(
            title='Database Explorer',
            sidebar_width=350,
            header_background='#0072B5',
            sidebar=pn.layout.Accordion(
                ('Database Explorer', sidebar_content),
                active=[0],
                sizing_mode='stretch_width'
            ),
            main=main_content
        )
        self.layout = template

    def show(self):
        return self.layout
