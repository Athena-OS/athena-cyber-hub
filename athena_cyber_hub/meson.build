pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'athena_cyber_hub')
gnome = import('gnome')

gnome.compile_resources('athena-cyber-hub',
  'athena-cyber-hub.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'athena-cyber-hub.in',
  output: 'athena-cyber-hub',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

subdir('backends')

athena_cyber_hub_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'program.py',
  'run_async.py',
  'container.py',
  'dialog_installation.py',
]

install_data(athena_cyber_hub_sources, install_dir: moduledir)
