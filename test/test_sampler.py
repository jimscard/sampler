from io import StringIO
from sampler.sampler import main
from unittest.mock import patch
from unittest.mock import patch, mock_open
import os
import pytest
import random
import secrets
import sys

class TestSampler:

    def test_empty_file(self):
        """
        Test that the main function handles an empty input file correctly.
        """
        empty_file = 'empty.csv'
        open(empty_file, 'w').close()  # Create an empty file
        
        with patch('sys.argv', ['sampler.py', empty_file]):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                assert fake_out.getvalue().strip() == '0 samples out of a population of 0 written to samples-empty.csv'
        
        os.remove(empty_file)  # Clean up
        os.remove('samples-empty.csv')

    def test_file_outside_current_directory(self):
        """
        Test that the main function raises a RuntimeError when the file path is outside the current working directory.
        """
        with patch('sys.argv', ['sampler.py', '../outside_file.csv']):
            with pytest.raises(RuntimeError, match='Filepath falls outside the base directory'):
                main()

    def test_file_with_insufficient_permissions(self):
        """
        Test that the main function handles a file with insufficient read permissions.
        """
        no_read_file = 'no_read.csv'
        with open(no_read_file, 'w') as f:
            f.write('test data')
        os.chmod(no_read_file, 0o000)  # Remove all permissions
        
        with patch('sys.argv', ['sampler.py', no_read_file]):
            with pytest.raises(PermissionError):
                main()
        
        os.chmod(no_read_file, 0o666)  # Restore permissions for cleanup
        os.remove(no_read_file)

    def test_file_with_non_ascii_characters(self):
        """
        Test that the main function handles a file with non-ASCII characters.
        """
        non_ascii_file = 'non_ascii.csv'
        with open(non_ascii_file, 'w', encoding='utf-8') as f:
            f.write('Column1,Column2\n')
            f.write('Value1,Value2\n')
            f.write('Värde1,Värde2\n')  # Non-ASCII characters
        
        with patch('sys.argv', ['sampler.py', non_ascii_file]):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                assert '3 samples out of a population of 3 written to samples-non_ascii.csv' in fake_out.getvalue()
        
        os.remove(non_ascii_file)  # Clean up
        os.remove('samples-non_ascii.csv')

    def test_main_1(self):
        """
        Test that main() prints an error message when no filename is provided.
        """
        with patch('sys.argv', ['sampler.py']):
            with patch('builtins.print') as mock_print:
                main()
                mock_print.assert_called_once_with('Please provide the filename of the CSV file as an argument')

    def test_main_2(self, monkeypatch, tmp_path):
        """
        Test that main() raises a RuntimeError when the filepath is outside the current working directory.
        """
        # Set up a temporary directory and file
        test_file = tmp_path / "test.csv"
        test_file.write_text("1,2,3\n4,5,6\n7,8,9\n")

        # Mock sys.argv to provide the filename
        monkeypatch.setattr(sys.argv, [sys.argv[0], str(test_file)])

        # Mock os.getcwd() to return a different directory
        monkeypatch.setattr(os, 'getcwd', lambda: str(tmp_path / "different_dir"))

        # Assert that RuntimeError is raised
        with pytest.raises(RuntimeError, match='Filepath falls outside the base directory'):
            main()

    def test_main_invalid_filepath(self):
        """
        Testcase 2 for def main():
        Test that main() raises a RuntimeError when given an invalid filepath.
        """
        # Mock sys.argv to provide an invalid filename
        sys.argv = [sys.argv[0], "/invalid/path/to/file.csv"]

        # Assert that RuntimeError is raised
        with pytest.raises(RuntimeError, match='Filepath falls outside the base directory'):
            main()

    def test_main_no_arguments(self):
        """
        Test that main() prints an error message when no filename is provided.
        """
        with patch('sys.argv', ['sampler.py']):
            with patch('builtins.print') as mock_print:
                main()
                mock_print.assert_called_once_with('Please provide the filename of the CSV file as an argument')

    def test_main_valid_file_and_sampling(self):
        """
        Test that main function correctly processes a valid CSV file,
        samples the lines, and writes the output file.
        """
        # Mock command line arguments
        test_filename = "test.csv"
        test_filepath = os.path.join(os.getcwd(), test_filename)
        
        # Create mock CSV content
        csv_content = "\n".join([f"line{i}" for i in range(100)])
        
        # Mock open function to return our test CSV content
        mock_file = mock_open(read_data=csv_content)
        
        with patch("sys.argv", ["sampler.py", test_filename]), \
             patch("os.path.abspath") as mock_abspath, \
             patch("os.path.realpath") as mock_realpath, \
             patch("builtins.open", mock_file), \
             patch("random.seed") as mock_seed, \
             patch("random.sample") as mock_sample, \
             patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            
            # Ensure the filepath is considered within the current working directory
            mock_abspath.return_value = test_filepath
            mock_realpath.return_value = test_filepath
            
            # Mock random sampling to return predictable results
            mock_sample.return_value = [f"line{i}" for i in range(25)]
            
            # Import the main function here to ensure mocks are in place
            
            # Call the main function
            main()
            
            # Verify that the file was opened for reading
            mock_file.assert_any_call(test_filepath, 'r', errors='ignore')
            
            # Verify that the output file was opened for writing
            mock_file.assert_any_call(f"samples-{test_filename}", 'w')
            
            # Verify that random.seed was called with a token
            mock_seed.assert_called_once()
            
            # Verify that random.sample was called with the correct arguments
            mock_sample.assert_called_once_with([f"line{i}\n" for i in range(100)], 25)
            
            # Verify the output message
            assert mock_stdout.getvalue().strip() == "25 samples out of a population of 100 written to samples-test.csv"
            
            # Verify that the sampled lines were written to the output file
            written_content = "".join(call.args[0] for call in mock_file().write.call_args_list)
            assert written_content == "".join([f"line{i}" for i in range(25)])

    def test_no_filename_provided(self):
        """
        Test that the main function prints an error message when no filename is provided.
        """
        with patch('sys.argv', ['sampler.py']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                assert fake_out.getvalue().strip() == 'Please provide the filename of the CSV file as an argument'

    def test_non_csv_file(self):
        """
        Test that the main function processes a non-CSV file without errors.
        """
        non_csv_file = 'test.txt'
        with open(non_csv_file, 'w') as f:
            f.write('This is not a CSV file\nBut it should still be processed')
        
        with patch('sys.argv', ['sampler.py', non_csv_file]):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                assert '2 samples out of a population of 2 written to samples-test.txt' in fake_out.getvalue()
        
        os.remove(non_csv_file)  # Clean up
        os.remove('samples-test.txt')

    def test_nonexistent_file(self):
        """
        Test that the main function raises a FileNotFoundError when the input file does not exist.
        """
        with patch('sys.argv', ['sampler.py', 'nonexistent_file.csv']):
            with pytest.raises(FileNotFoundError):
                main()