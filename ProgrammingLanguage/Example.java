package org.example;


import java.util.Random;

public class Example {

    public static void main(String[] args) {
        int size = 10;
        int[] array = generateRandomArray(size);

        System.out.println("Random array:");
        printArray(array);
    }

    public static int[] generateRandomArray(int size) {
        int[] array = new int[size];
        Random random = new Random();
        for (int i = 0; i < size; i++) {
            array[i] = random.nextInt(100); // Generate random integers between 0 and 99
        }
        return array;
    }

    public static void printArray(int[] array) {
        for (int num : array) {
            System.out.print(num + " ");
        }
        System.out.println();
    }
}
