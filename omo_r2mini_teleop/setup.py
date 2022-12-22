from setuptools import setup

package_name = 'omo_r2mini_teleop'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Dr.K',
    maintainer_email='kucira00@gmail.com',
    description='Teleoperation node using keyboard for omo_r2mini.',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'teleop_keyboard = omo_r2mini_teleop.teleop_keyboard:main'
        ],
    },
)
