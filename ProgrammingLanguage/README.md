Step 1: Download intelli J DEA Community version
Step 2: Install Plugins by Go to Settings -> Plugins -> Search ANTLR and install the plugin by Terrence
Step 3: Go to File -> New -> Create Project -> Create using these settings:
  Language: Java
  Build System: Maven
  JDK: (newest is fine)

Step 4: Copy and paste code below to your pom.xml file:
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>org.example</groupId>
    <artifactId>ASTParser</artifactId>
    <version>1.0-SNAPSHOT</version>

    <properties>
        <maven.compiler.source>21</maven.compiler.source>
        <maven.compiler.target>21</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <!-- Other dependencies -->
        <!-- https://mvnrepository.com/artifact/com.google.code.gson/gson -->
        <dependency>
            <groupId>com.google.code.gson</groupId>
            <artifactId>gson</artifactId>
            <version>2.10.1</version>
        </dependency>
        <dependency>
            <groupId>org.antlr</groupId>
            <artifactId>antlr4-runtime</artifactId>
            <version>4.13.1</version> <!-- or the latest version -->
        </dependency>
    </dependencies>
</project>

Step 5: Add files: Main.java, Example.java, Expression.g4 to same java folder of the project
//Change the path of the Example file to where you saved it for example:
            File inputFile = new File("/Users/Kevin/IdeaProjects/AST/src/main/java/org/example/Example.java");

//This can be done by right click the file and copy as absolute path, change the separator to the one suitable for your system
Step 6: Right click the Expression.g4 and click Configure ANTLR...and paste below path to "Output directory where....is generated"
ASTParser\ASTParser\src\main\java\org\example
Step 7: Right click the Expression.g4. Then click Generate ANTLR Recognizer.
Step 8: Run the main file to get the AST tree.
