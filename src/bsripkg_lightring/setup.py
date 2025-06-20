from setuptools import find_packages, setup

package_name = 'bsripkg_lightring'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='juan',
    maintainer_email='juanjuo37@gmail.com',
    description='Uses Create3\'s Button1 to display colors in the lightring',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'bsri_node_lightring_test = bsripkg_lightring.bsri_node_lightring_test:main',
            'bsri_node_lightring_pulse = bsripkg_lightring.bsri_node_lightring_pulse:main',
        ],
    },
)
