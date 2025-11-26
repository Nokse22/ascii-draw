pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'ascii_draw')
gnome = import('gnome')

pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())

gnome.compile_resources('ascii-draw',
  'ascii-draw.gresource.xml',
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
  input: 'ascii-draw.in',
  output: 'ascii-draw',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr--r--'
)

ascii_draw_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'palette.py',
  'new_palette_window.py',
]

install_data(ascii_draw_sources, install_dir: moduledir)

install_subdir('.', install_dir: moduledir)

subdir('icons')