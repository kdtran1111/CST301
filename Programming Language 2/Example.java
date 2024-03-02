// Import statements
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

public class Example {
    public static void main(String[] args) {
        // Example usage of the imported packages
        List<String> names = new ArrayList<>();
        names.add("Alice");
        names.add("Bob");
        names.add("Charlie");

        System.out.println("Names: " + names);

        Random rand = new Random();
        int randomNumber = rand.nextInt(100);
        System.out.println("Random number: " + randomNumber);

        LocalDate currentDate = LocalDate.now();
        System.out.println("Current date: " + currentDate);

        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd-MM-yyyy");
        String formattedDate = currentDate.format(formatter);
        System.out.println("Formatted date: " + formattedDate);
    }
}
