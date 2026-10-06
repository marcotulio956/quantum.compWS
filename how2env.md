## Install Lib dependencies
````
# env recommended for quantum comp. stuff
python3 -m venv ~/py_envs
source ~/py_envs/bin/activate
python3 prediction.py
python3 -m pip install pyarrow pandas numpy pathlib ket quiskit quiskit_aer
````

## Notebook Use
````
(py_envs) $ pip install jupyter-notebook
(py_envs) $ jupyter notebook <notebook>.ipynb
````
- if you use Jupyter extensions for vscode, note the process forwarded addrs  (ex: 127.0.0.1:8888), and change python kernel to the existing running server so it loads env (ex: home/<user>/py_envs/bin/python3/, /home/<user>/py_envs/bin/jupyter-notebook)

- you notebook password is the token created when lunching the process (ex:  localhost:8888/tree?token=<token48>), you can ignore passwords by running with flags: 
````jupyter notebook --ip='*' --NotebookApp.token='' --NotebookApp.password=''````

- if you use vscode you can simply select you python kernel to source your prefered .env