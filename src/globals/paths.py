import pathlib

# ============================================== #
# DATABASE
# ============================================== #

database = dict(name = 'iam-diagnostics-internal',
                username = 'none',
                password = 'none')

base = pathlib.Path(__file__).parent.parent.parent
figures = base / 'Figures'
figures_Xdrive = pathlib.Path("X:/user/dekkerm/figure_sharing/iamc-diagnostics/2026_Nov/")

data = base / 'data' / 'iamc-diagnostics'
