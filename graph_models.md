# How to Graph Models in Django
#### _By Matt Getgen_

## Instructions

1. Install these system packages: `python3-dev graphviz libgraphviz-dev pkg-config` using your package 
manager. I'm using `apt` with linux.
```
sudo apt install python3-dev graphviz libgraphviz-dev pkg-config
```
2. Install python packages within your environment: `python -m pip install django-extensions pygraphviz --use-pep517`

3. In your `settings.py` file, add this to your `INSTALLED_APPS` section:
```python
INSTALLED_APPS = [
    ...
    'django_extensions',
]
```
> You will be able to see this difference if you run `python manage.py help` and see a list of `django_extensions` commands.

4. Also in your `settings.py` file, add some rules for the `graph_models` extension.
```python
GRAPH_MODELS = {
    'app_labels': ['bassett', 'accounts'],	# these arem my apps, yours may differ.
    'group_models': False	# if you want to group the models based on application, set True.
```

5. Finally, run `python manage.py graph_models --arrow-shape normal -o <file_name>.png`
	> You can view other arguments by running `python manage.py graph_models -h`
