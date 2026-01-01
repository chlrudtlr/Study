CXX      := g++
CXXFLAGS := -std=c++17 -Wall -Wextra -O2
BIN_DIR  := bin

SRCS := $(wildcard *.cpp)
BINS := $(SRCS:.cpp=)

.PHONY: all clean

all: $(BIN_DIR) $(BINS:%=$(BIN_DIR)/%)

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

$(BIN_DIR)/%: %.cpp
	$(CXX) $(CXXFLAGS) -o $@ $<

clean:
	rm -rf $(BIN_DIR)
