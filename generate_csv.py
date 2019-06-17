from core.utils import build_indices_csv, build_indices

def generate_csv():
    subjects = [r'C:\Users\Pedro\Documents\Shared\results\result_BCK',
                r'C:\Users\Pedro\Documents\Shared\results\result_commons-lang',
                r'C:\Users\Pedro\Documents\Shared\results\result_commons-math',
                r'C:\Users\Pedro\Documents\Shared\results\result_joda-time']
    build_indices_csv(subjects)
    build_indices(subjects)


generate_csv()