import argparse
import logging
import os
import paramiko
from stat import S_ISDIR

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Main function
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remote file search')
    parser.add_argument('--host', required=True, help='Host address')
    parser.add_argument('--port', type=int, default=22, help='Port number')
    parser.add_argument('--user', required=True, help='Username')
    parser.add_argument('--password', required=True, help='Password')
    parser.add_argument('--procedure', required=True, help='Procedure to execute')
    parser.add_argument('--paths', nargs='+', help='Paths to search')
    parser.add_argument('--extensions', nargs='+', help='File extensions to search for')
    parser.add_argument('--max-size-mb', type=int, help='Max size of files to search in MB')

    args = parser.parse_args()

    # Connecting to the remote server
    try:
        transport = paramiko.Transport((args.host, args.port))
        transport.connect(username=args.user, password=args.password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        # File searching and processing logic goes here
        for path in args.paths:
            if S_ISDIR(sftp.stat(path).st_mode):
                logging.INFO(f'Processing directory: {path}')
                for dirpath, dirnames, filenames in sftp.walk(path):
                    for filename in filenames:
                        if filename.endswith(tuple(args.extensions)):
                            file_path = os.path.join(dirpath, filename)
                            logging.INFO(f'Found file: {file_path}')
                            # Read file in chunks
                            with sftp.open(file_path, 'rb') as remote_file:
                                while True:
                                    chunk = remote_file.read(1024)
                                    if not chunk:
                                        break
                                    # Process chunk
                            
            else:
                logging.WARN(f'Path is not a directory: {path}')

    except Exception as e:
        logging.ERROR(f'Error during processing: {e}')
    finally:
        transport.close()  # Ensure resources are closed
