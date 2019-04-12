/*----------------------------------------------------------------------------*/
/* Copyright (c) 2017-2018 FIRST. All Rights Reserved.                        */
/* Open Source Software - may be modified and shared by FRC teams. The code   */
/* must be accompanied by the FIRST BSD license file in the root directory of */
/* the project.                                                               */
/*----------------------------------------------------------------------------*/

package frc.robot;

import edu.wpi.first.wpilibj.IterativeRobot;
import edu.wpi.first.wpilibj.smartdashboard.SendableChooser;
import edu.wpi.first.wpilibj.smartdashboard.SmartDashboard;
import edu.wpi.first.networktables.*;
import java.io.*;
import java.net.*;
import java.util.*;
import edu.wpi.cscore.UsbCamera;
import edu.wpi.first.cameraserver.CameraServer;


/**
 * The VM is configured to automatically run this class, and to call the
 * functions corresponding to each mode, as described in the IterativeRobot
 * documentation. If you change the name of this class or the package after
 * creating this project, you must also update the build.gradle file in the
 * project.
 */
public class Robot extends IterativeRobot {
  private static final String kDefaultAuto = "Default";
  private static final String kCustomAuto = "My Auto";
  private String m_autoSelected;
  private final SendableChooser<String> m_chooser = new SendableChooser<>();
  

  NetworkTableEntry gotit;
  NetworkTableEntry copy;
  NetworkTableEntry resolution;
  NetworkTableEntry fps;
  NetworkTableEntry distance;
 

  /**
   * This function is run when the robot is first started up and should be
   * used for any initialization code.
   */
  @Override
  public void robotInit() {
    UsbCamera camera = CameraServer.getInstance().startAutomaticCapture();
      // Set the resolution
    camera.setResolution(500, 500);

    m_chooser.setDefaultOption("Default Auto", kDefaultAuto);
    m_chooser.addOption("My Auto", kCustomAuto);
    SmartDashboard.putData("Auto choices", m_chooser);
    SmartDashboard.putString("hello", "hi");
    NetworkTableInstance inst = NetworkTableInstance.getDefault();
    NetworkTable table = inst.getTable("/SmartDashboard");
    gotit = table.getEntry("example_variable");
    copy = table.getEntry("hello");
    resolution = table.getEntry("resolution");
    fps = table.getEntry("fps");
    distance = table.getEntry("distance");


  }

  /**
   * This function is called every robot packet, no matter the mode. Use
   * this for items like diagnostics that you want ran during disabled,
   * autonomous, teleoperated and test.
   *
   * <p>This runs after the mode specific periodic functions, but before
   * LiveWindow and SmartDashboard integrated updating.
   */
  @Override
  public void robotPeriodic() {
  }

  /**
   * This autonomous (along with the chooser code above) shows how to select
   * between different autonomous modes using the dashboard. The sendable
   * chooser code works with the Java SmartDashboard. If you prefer the
   * LabVIEW Dashboard, remove all of the chooser code and uncomment the
   * getString line to get the auto name from the text box below the Gyro
   *
   * <p>You can add additional auto modes by adding additional comparisons to
   * the switch structure below with additional strings. If using the
   * SendableChooser make sure to add them to the chooser code above as well.
   */
  @Override
  public void autonomousInit() {
    m_autoSelected = m_chooser.getSelected();
    // autoSelected = SmartDashboard.getString("Auto Selector",
    // defaultAuto);
    System.out.println("Auto selected: " + m_autoSelected);
  }

  /**
   * This function is called periodically during autonomous.
   */
  @Override
  public void autonomousPeriodic() {
    switch (m_autoSelected) {
      case kCustomAuto:
        // Put custom auto code here
        break;
      case kDefaultAuto:
      default:
        // Put default auto code here
        break;
    }
  }

  /**
   * This function is called periodically during operator control.
   */
  @Override
  public void teleopPeriodic() {
    // SmartDashboard.putString("my name", "James");
    // SmartDashboard.putBoolean("my boolean", false);
    // boolean mytext = SmartDashboard.getBoolean("example_variable", true);
    // SmartDashboard.putBoolean("got it:", mytext);
    // SmartDashboard.putString("new name", SmartDashboard.getString("my name", "bob"));
    // SmartDashboard.putBoolean("reallygotit:", gotit.getBoolean(false));
    try {
      //while(true) {
        String resolutionValue = resolution.getString("a");
        String fpsValue = fps.getString("a");
        byte[] data = resolutionValue.getBytes();
        byte[] data2 = fpsValue.getBytes();
        DatagramPacket packet2 = new DatagramPacket(data, data.length, InetAddress.getByName("10.54.77.85"), 4446);
        DatagramPacket packet3 = new DatagramPacket(data2, data2.length, InetAddress.getByName("10.54.77.85"), 4446);
        new DatagramSocket().send(packet2);
        new DatagramSocket().send(packet3);
        DatagramSocket socket = new DatagramSocket(4445);
        byte[] buffer = new byte[1024];
        DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
        socket.receive(packet);
        String str = new String(packet.getData(), 0, packet.getLength());
        copy.setString(str);
        System.out.print(str);
        socket.close();
      //}
    } catch (Exception e) {
      //e.printStackTrace();
      System.out.print("hi there");
    }
  }

  /**
   * This function is called periodically during test mode.
   */
  @Override
  public void testPeriodic() {
  }
}
