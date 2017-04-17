from distutils.core import setup
import wtty

setup(
    name = wtty.NAME,
    version = wtty.VERSION,
    description = wtty.DESCR,
    long_description = wtty.DESCR_LONG, 
    author = wtty.AUTHOR,
    author_email = wtty.AUTHOR_EMAIL,
    url = wtty.URL,
    packages = ['wtty'],
    package_data = {'wtty' : ["templates/*"]},
    scripts = ["wtty-iod", "wtty-appd"],
)

