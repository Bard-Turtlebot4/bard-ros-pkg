from setuptools import find_packages, setup

package_name = 'bsripkg_edit_display'

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
    description='Writes on Turtlebot4 Display',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'turtlebot4_display_node = bsripkg_edit_display.turtlebot4_display_node:main'
        ],
    },
)
