import os
import zipfile
from pathlib import Path

def create_submission_zip(repo_root: Path = None, output_zip_path: Path = None) -> Path:
    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent.parent
    if output_zip_path is None:
        output_zip_path = repo_root / 'code.zip'

    print(f'Creating submission zip at: {output_zip_path}')
    
    include_dirs = [
        'code',
        'dataset',
        'evaluation'
    ]
    include_files = [
        'output.csv',
        'sample_output.csv',
        'README.md',
        'problem_statement.md',
        'AGENTS.md',
        'package.json'
    ]
    
    exclude_substrings = [
        '__pycache__',
        '.pyc',
        '.pyo',
        '.env',
        '.git',
        'node_modules',
        'dist',
        '.system_generated'
    ]
    
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for dir_name in include_dirs:
            dir_path = repo_root / dir_name
            if not dir_path.exists():
                print(f'Warning: Directory {dir_path} does not exist!')
                continue
            for file_path in dir_path.rglob('*'):
                if file_path.is_file():
                    str_path = file_path.as_posix()
                    if any(ex in str_path for ex in exclude_substrings):
                        continue
                    arcname = file_path.relative_to(repo_root).as_posix()
                    zipf.write(file_path, arcname)
                    
        for fname in include_files:
            file_path = repo_root / fname
            if file_path.exists() and file_path.is_file():
                arcname = file_path.relative_to(repo_root).as_posix()
                zipf.write(file_path, arcname)
            else:
                print(f'Notice: Root file {fname} not found or skipped.')

    file_size_mb = output_zip_path.stat().st_size / (1024 * 1024)
    print(f'Successfully packaged {output_zip_path} ({file_size_mb:.2f} MB)')
    return output_zip_path

if __name__ == '__main__':
    create_submission_zip()
