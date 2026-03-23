import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    # 1. Setup Paths
    bringup_pkg = get_package_share_directory('titan_bringup')
    nav2_pkg = get_package_share_directory('nav2_bringup')
    
    # Declare Launch Arguments
    map_arg = DeclareLaunchArgument(
        'map',
        description='Full path to map yaml file'
    )

    nav2_params = os.path.join(bringup_pkg, 'config', 'nav2_params.yaml')

    # 2. Include Bringup Launch (Hardware + URDF)
    bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_pkg, 'launch', 'bringup.launch.py')
        )
    )

    # 3. Include Nav2 Bringup (AMCL, Planner, Controller)
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_pkg, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'map': LaunchConfiguration('map'),
            'use_sim_time': 'false',
            'params_file': nav2_params,
            'autostart': 'true'
        }.items()
    )

    return LaunchDescription([
        map_arg,
        bringup_launch,
        nav2_launch
    ])