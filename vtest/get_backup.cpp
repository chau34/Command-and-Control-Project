#include "httplib.h"
#include <fstream>
#include <iostream>

int main() {
    httplib::Server server;

    server.Post("/upload", [](const httplib::Request& req, httplib::Response& res) {
        std::cout << "Received " << req.body.size() << " bytes\n";
        std::ofstream out("cat.jpg", std::ios::binary);
        out.write(req.body.data(), req.body.size());
        out.close();
        res.set_content("received", "text/plain");
    });

    if (!server.listen("127.0.0.1", 8443)) {
        std::cerr << "Could not listen on port 8443\n";
        return 1;
    }
}