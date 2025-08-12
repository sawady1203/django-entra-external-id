# django-entra-external-id
Entra External ID と Django を連携させるまでのリポジトリです

初手の環境構築
```sh
$ uv init .
$ rm main.py
$ uv add django
$ uv run django-admin startproject config .
$ uv run python manage.py runserver
```

django-dotenv で環境変数を設定
```sh
$ uv add python-dotenv
$ touch .env
```