from setuptools import setup

setup(
    name='django-phantom-theme',
    version=__import__('phantom').VERSION,
    description='Phantom is theme for django admin with many widgets, based on Twitter bootstrap 3.x.',
    author='QQWDG',
    author_email='support@eggforsale.com',
    url='http://eggforsale.com',
    packages=['phantom', 'phantom.templatetags'],
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'License :: Free for non-commercial use',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Topic :: Software Development',
        'Topic :: Software Development :: User Interfaces',
    ]
)
