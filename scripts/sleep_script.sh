#!/bin/bash

# Sprawdź czy podano argument
if [ $# -eq 0 ]; then
    echo "Użycie: $0 <liczba_sekund>"
    exit 1
fi

# Pobierz liczbę sekund z pierwszego argumentu
seconds=$1

# Sprawdź czy argument to liczba
if ! [[ "$seconds" =~ ^[0-9]+$ ]]; then
    echo "Błąd: Argument musi być liczbą całkowitą"
    exit 1
fi

# Wykonaj sleep na podaną liczbę sekund
sleep $seconds