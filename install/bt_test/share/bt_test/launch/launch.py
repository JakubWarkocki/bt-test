import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from nav2_common.launch import RewrittenYaml


def generate_launch_description():

    package_name = 'bt_test'  # Change this to your package name

    # Paths to various files
    gazebo_params_file = os.path.join(get_package_share_directory(package_name), 'config', 'gazebo_params.yaml')
    world_file_name = 'basic.world'
    world_file_path = os.path.join(get_package_share_directory(package_name), 'worlds', world_file_name)

    # Include robot_state_publisher launch file
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(package_name), 'launch', 'rsp.launch.py'
        )]), launch_arguments={'use_sim_time': 'true', 'use_ros2_control': 'true'}.items()
    )

    # Include EKF localization launch file
    ekf_navsat = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(package_name), 'launch', 'dual_ekf_navsat.launch.py'
        )])
    )

    # Include the Gazebo launch file
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py'
        )]),
        launch_arguments={'world': world_file_path, 'extra_gazebo_args': '--ros-args --params-file ' + gazebo_params_file}.items()
    )

    # Run the spawner node to spawn the robot in Gazebo
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=[
                            '-topic',
                            'robot_description',
                            '-entity',
                            'my_bot'
                            ],
                        output='screen')

    # Spawn differential drive controller
    diff_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_cont"],
    )

    # Spawn joint state broadcaster
    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad"],
    )
    

    keyboard = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','keyboard.launch.py'
                )]), launch_arguments={'use_sim_time': 'true'}.items()
    )
    nav2_params = os.path.join(get_package_share_directory(package_name), 'config', 'nav2_params.yaml')
    configured_params = RewrittenYaml(
        source_file=nav2_params, root_key="", param_rewrites="", convert_types=True
    )
    # Include the Nav2 bringup launch file
    nav2_launch_file = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('nav2_bringup'), 'launch', 'navigation_launch.py'
        )]),
        launch_arguments={
            'use_sim_time': 'true',
            'params_file': configured_params,
            "autostart": "True",
        }.items()
    )

    # Return the LaunchDescription
    return LaunchDescription([
        gazebo,
        spawn_entity,
        rsp,
        diff_drive_spawner,
        joint_broad_spawner,
        ekf_navsat,
        nav2_launch_file
    ])
