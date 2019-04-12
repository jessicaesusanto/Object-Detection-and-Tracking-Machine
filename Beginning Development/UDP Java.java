import java.io.*;
import java.net.*;
import java.util.*;

public class UDPTest {

    
    public static void main(String[] args) throws Exception  {
        DatagramSocket socket = new DatagramSocket(4445);
        
        while (true) {
           byte[] data = "Hello".getBytes();
           DatagramPacket packet2 = new DatagramPacket(data, data.length, InetAddress.getByName("10.50.6.151"), 4446);
           new DatagramSocket().send(packet2);
           byte[] buffer = new byte[512];
           DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
           socket.receive(packet);
           String str = new String(packet.getData(), 0, packet.getLength());
           System.out.println(str);
           
           
        }
        // socket.close();
    }

}