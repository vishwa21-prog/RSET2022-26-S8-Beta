from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    pkg_description = get_package_share_directory('titan_description')
    
    
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(pkg_description, 'launch', 'rsp.launch.py')]),
        launch_arguments={'use_sim_time': 'false'}.items()
    )

    
    lidar_node = Node(...)

    return LaunchDescription([rsp, lidar_node])