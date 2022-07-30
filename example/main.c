#include "toggle.h"
#include <stdio.h>

void print_lcd(void)
{
    if (LCD_SIZE == LCD_1602)
    {
        printf("+----------------+\n");
        printf("|LCD 16x2        |\n");
        printf("|                |\n");
        printf("+----------------+\n");
    }
    else if (LCD_SIZE == LCD_2004)
    {
        printf("+--------------------+\n");
        printf("|LCD 20x4            |\n");
        printf("|                    |\n");
        printf("|                    |\n");
        printf("|                    |\n");
        printf("+--------------------+\n");
    }
    else
    {
        printf("ERROR: Unknown LCD_SIZE\n");
    }
}

int main(void)
{
    if (DEBUG_PRINT)
        printf("DEBUG: main: begin\n");

    print_lcd();

#if (TESTING)
    {
        printf("TEST: main: changing display from %dx%d", LCD_COLS, LCD_LINES);

        /* It is possible to modify OPTIONs when TESTING=1. */
        LCD_COLS = 20;
        LCD_LINES = 4;

        printf(" to %dx%d\n", LCD_COLS, LCD_LINES);

        print_lcd();
    }
#endif

    if (DEBUG_PRINT)
        printf("DEBUG: main: end\n");

    return 0;
}
