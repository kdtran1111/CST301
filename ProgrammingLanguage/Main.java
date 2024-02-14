package org.example;

import org.antlr.v4.runtime.CharStreams;
import org.antlr.v4.runtime.CommonTokenStream;
import org.example.ExpressionLexer;
import org.example.ExpressionParser;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileWriter;
import java.io.IOException;
import org.antlr.v4.runtime.CharStreams;
import org.antlr.v4.runtime.CommonTokenStream;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import org.antlr.v4.runtime.Token;
import org.antlr.v4.runtime.tree.ParseTree;
import org.antlr.v4.runtime.tree.TerminalNodeImpl;

import java.util.*;

public class Main {

    private static final Gson PRETTY_PRINT_GSON = new GsonBuilder().setPrettyPrinting().create();
    private static final Gson GSON = new Gson();

    public static String toJson(ParseTree tree) {
        return toJson(tree, true);
    }

    public static String toJson(ParseTree tree, boolean prettyPrint) {
        return prettyPrint ? PRETTY_PRINT_GSON.toJson(toMap(tree)) : GSON.toJson(toMap(tree));
    }

    public static Map<String, Object> toMap(ParseTree tree) {
        Map<String, Object> map = new LinkedHashMap<>();
        traverse(tree, map);
        return map;
    }

    public static void traverse(ParseTree tree, Map<String, Object> map) {
        if (tree instanceof TerminalNodeImpl) {
            Token token = ((TerminalNodeImpl) tree).getSymbol();
            map.put("type", token.getType());
            map.put("text", token.getText());
        } else {
            List<Map<String, Object>> children = new ArrayList<>();
            String name = tree.getClass().getSimpleName().replaceAll("Context$", "");
            map.put(Character.toLowerCase(name.charAt(0)) + name.substring(1), children);

            for (int i = 0; i < tree.getChildCount(); i++) {
                Map<String, Object> nested = new LinkedHashMap<>();
                children.add(nested);
                traverse(tree.getChild(i), nested);
            }
        }
    }

    public static void main(String[] args) {
        try {
            File inputFile = new File("/Users/Kevin/IdeaProjects/AST/src/main/java/org/example/Example.java");
            FileInputStream fileInputStream = new FileInputStream(inputFile);
            ExpressionLexer lexer = new ExpressionLexer(CharStreams.fromStream(fileInputStream));
            ExpressionParser parser = new ExpressionParser(new CommonTokenStream(lexer));

            // Convert AST to JSON
            String json = toJson(parser.compilationUnit());

            // Write JSON to file
            File outputFile = new File("output.json");
            FileWriter writer = new FileWriter(outputFile);
            writer.write(json);
            writer.close();

            System.out.println("JSON written to output.json");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    // Define your toJson method here
    private static String toJson(Object obj) {
        // Implement your toJson method here
        return ""; // Placeholder for the actual implementation
    }
}