Código criado utilizando a linguagem [Python](https://www.python.org), ela é necessária para a compilação do código. Caso não tenha a linguagem intale ela no seguinte link: https://apps.microsoft.com/detail/9ncvdn91xzqp?hl=en-us&gl=US.

## Pré requisitos
- [Python](https://www.python.org)
- [Cmake](https://github.com/Kitware/CMake/releases/download/v3.29.2/cmake-3.29.2-windows-x86_64.msi) (Necessário para a instalação do dlib & face_recognition)
- [Visual Studio](https://visualstudio.microsoft.com/pt-br/thank-you-downloading-visual-studio/?sku=Community&channel=Release&version=VS2022&source=VSLandingPage&cid=2030&passive=false) (Config de desenvolvimento C++, dentro do instalador)
- OpenCV

## Instalação / Configuração
```
$ python -m venv .venv
$ .\.venv\Scripts\activate
```
### Instalação das dependencias
```
$ pip install -r .\requirements.txt
```
### Crie o arquivo .env
```
$ touch .env
```
###
#### Adicione o conteudo abaixo ao arquivo criado:
```
ODDO_URL=http://localhost:8069/ (LINK ODOO LOCAL)
DB_ODOO=(NOME DO DATABASE DO ODOO LOCAL)
USER_ODOO=(NOME DO USUARIO ADM DO SISTEMA)
PASS_ODOO=(SENHA DO USUARIO ADM)
URL_RTSP=(LINK DO LINK RTSP DA CAMERA)
```