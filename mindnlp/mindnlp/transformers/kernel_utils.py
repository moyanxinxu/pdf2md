# Copyright 2022 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""utils for kernel compile"""

import os
import subprocess
from pathlib import Path
import mindspore
from mindnlp.utils import logging

logger = logging.get_logger(__name__)


def _find_cuda_home():
    """
    Find the CUDA home directory.
    
    This function searches for the CUDA home directory on the system.
    It first checks the environment variables 'CUDA_HOME' and 'CUDA_PATH' to see if either of them is set.
    If not, it tries to locate the 'nvcc' executable using the 'which' command and extracts the CUDA home
    directory path from it.
    
    Returns:
        str: The path to the CUDA home directory. Returns None if the CUDA home directory is not found.
    
    Raises:
        CalledProcessError: If the 'which' command fails to locate the 'nvcc' executable.
    
    Note:
        This function assumes that CUDA is installed on the system and the 'nvcc' command is available.
    
    """
    cuda_home = os.environ.get('CUDA_HOME') or os.environ.get('CUDA_PATH')
    if cuda_home is None:
        try:
            nvcc = subprocess.check_output(['which', 'nvcc']).decode().rstrip('\r\n')
            cuda_home = os.path.dirname(os.path.dirname(nvcc))
        except subprocess.CalledProcessError as exc:
            logger.warning("CUDA Not Available")
    return cuda_home


def _get_nvcc_info(cuda_home):
    """
    This function retrieves the nvcc information for the specified CUDA installation.
    
    Args:
        cuda_home (str): The path to the CUDA installation directory.
    
    Returns:
        None: If the nvcc information cannot be retrieved or if the CUDA installation directory is invalid.
    
    Raises:
        subprocess.SubprocessError: If an error occurs while executing the 'nvcc -V' command.
    
    Note:
        The 'nvcc' command is used to compile CUDA programs and is typically found in the 'bin' directory of the CUDA installation.
        This function checks if the 'nvcc' command is available by executing 'nvcc -V' and returns the full path to 'nvcc'
        if the command is found and no errors occur. Otherwise, it returns None and logs a warning message.
    """
    nvcc = None
    if cuda_home is not None and os.path.isdir(cuda_home):
        try:
            nvcc = os.path.join(cuda_home, 'bin/nvcc')
            subprocess.check_output(f"{nvcc} -V", shell=True)
        except subprocess.SubprocessError as exc:
            logger.warning("NVCC Not Available")
    return nvcc

ENV_INFO = {}
CUDA_HOME = _find_cuda_home() if mindspore.get_context('device_target') =='GPU' else None
ENV_INFO['cuda_home'] = CUDA_HOME
ENV_INFO['NVCC'] = _get_nvcc_info(CUDA_HOME)

def compile_kernel(kernel_name, **kwargs):
    """compile kernel and return so file path"""
    kernel_folder = Path(__file__).resolve().parent.parent / "_csrc" / "cuda"
    cuda_kernel_file = kernel_folder / f'{kernel_name}.cu'
    cuda_so_file = kernel_folder / f'{kernel_name}.so'
    if cuda_so_file.exists():
        return cuda_so_file

    flags = [
        "--shared",
        "-Xcompiler",
        "-fPIC",
        "-res-usage",
        "--maxrregcount 60",
        "--use_fast_math",
        "-O3",
        "-Xptxas -O3",
        "--extra-device-vectorization"
    ]

    for key, value in kwargs.items():
        flags.append(f'-D{key}={value}')

    # Construct nvcc command-line arguments
    nvcc_args = [ENV_INFO['NVCC'], str(cuda_kernel_file), '-o', str(cuda_so_file)]

    nvcc_command = ' '.join(nvcc_args + flags)
    # Execute nvcc compilation command
    print(nvcc_command)
    result = subprocess.run(nvcc_command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        logger.info('Compilation successful')
    else:
        error_message = result.stderr.decode()
        raise RuntimeError('Compilation failed:', error_message)

    return cuda_so_file
